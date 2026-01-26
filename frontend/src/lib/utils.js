import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
}

export function formatTimeRemaining(endsAt) {
  const now = new Date();
  const end = new Date(endsAt);
  const diff = end - now;

  if (diff <= 0) {
    return { text: 'Ended', isUrgent: false, isEnded: true };
  }

  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((diff % (1000 * 60)) / 1000);

  const isUrgent = diff < 3600000; // Less than 1 hour

  if (days > 0) {
    return { text: `${days}d ${hours}h`, isUrgent: false, isEnded: false };
  } else if (hours > 0) {
    return { text: `${hours}h ${minutes}m`, isUrgent, isEnded: false };
  } else if (minutes > 0) {
    return { text: `${minutes}m ${seconds}s`, isUrgent: true, isEnded: false };
  } else {
    return { text: `${seconds}s`, isUrgent: true, isEnded: false };
  }
}

export function formatRelativeTime(date) {
  const now = new Date();
  const then = new Date(date);
  const diff = now - then;

  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (days > 0) return `${days}d ago`;
  if (hours > 0) return `${hours}h ago`;
  if (minutes > 0) return `${minutes}m ago`;
  return `${seconds}s ago`;
}