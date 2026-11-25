import { API_BASE_URL, getAuthHeaders } from "./api";

export function isNotificationSupported(): boolean {
  return "Notification" in window && "serviceWorker" in navigator;
}

export async function registerServiceWorker(): Promise<ServiceWorkerRegistration | null> {
  if (!("serviceWorker" in navigator)) return null;
  try {
    return await navigator.serviceWorker.register("./sw.js");
  } catch (err) {
    console.warn("No se pudo registrar el Service Worker:", err);
    return null;
  }
}

export async function requestNotificationPermission(): Promise<NotificationPermission> {
  if (!isNotificationSupported()) return "denied";
  return Notification.requestPermission();
}

function urlBase64ToUint8Array(base64String: string): Uint8Array<ArrayBuffer> {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(new ArrayBuffer(rawData.length));
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

async function fetchVapidPublicKey(): Promise<string> {
  const envKey = import.meta.env.VITE_VAPID_PUBLIC_KEY;
  if (envKey) return envKey;
  try {
    const resp = await fetch(`${API_BASE_URL}/api/v1/notifications/vapid-public-key`, {
      headers: getAuthHeaders(),
    });
    if (!resp.ok) return "";
    const data = (await resp.json()) as { publicKey?: string };
    return data.publicKey || "";
  } catch {
    return "";
  }
}

export async function subscribeToWebPush(): Promise<{
  permission: NotificationPermission;
  subscribed: boolean;
}> {
  const permission = await requestNotificationPermission();
  if (permission !== "granted") {
    return { permission, subscribed: false };
  }

  const registration = await navigator.serviceWorker.ready;
  const vapidPublicKey = await fetchVapidPublicKey();

  if ("PushManager" in window && vapidPublicKey) {
    try {
      let subscription = await registration.pushManager.getSubscription();
      if (!subscription) {
        subscription = await registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: urlBase64ToUint8Array(vapidPublicKey),
        });
      }

      const json = subscription.toJSON();
      if (json.endpoint && json.keys) {
        await fetch(`${API_BASE_URL}/api/v1/notifications/subscribe`, {
          method: "POST",
          headers: { "Content-Type": "application/json", ...getAuthHeaders() },
          body: JSON.stringify({
            endpoint: json.endpoint,
            keys: json.keys,
            userAgent: navigator.userAgent,
          }),
        });
        return { permission, subscribed: true };
      }
    } catch (err) {
      console.warn("No se pudo completar suscripción Web Push, usando notificación local:", err);
    }
  }

  await registration.showNotification("ShopIA", {
    body: "Notificaciones locales activadas (v003-a).",
    icon: "./icons/icon.svg",
  });
  return { permission, subscribed: false };
}

export async function triggerBackendTestPush(): Promise<boolean> {
  try {
    const resp = await fetch(`${API_BASE_URL}/api/v1/notifications/test`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...getAuthHeaders() },
      body: JSON.stringify({
        title: "ShopIA · v003-a",
        body: "Notificación Web Push real recibida desde tu backend local.",
        url: "./",
      }),
    });
    if (!resp.ok) return false;
    const data = (await resp.json()) as { sent?: number };
    return (data.sent || 0) > 0;
  } catch {
    return false;
  }
}
