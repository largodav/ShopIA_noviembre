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

export async function sendLocalTestNotification(): Promise<void> {
  if (!isNotificationSupported() || Notification.permission !== "granted") return;
  const registration = await navigator.serviceWorker.ready;
  await registration.showNotification("ShopIA", {
    body: "Notificaciones del sistema activadas correctamente (v001-a).",
    icon: "./icons/icon.svg",
  });
}
