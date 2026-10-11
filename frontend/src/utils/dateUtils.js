/**
 * Shared Date and Time Utilities for Local Timezone Handling
 */

/**
 * Formats an ISO datetime string into the user's local timezone representation.
 * Uses 'en-IN' locale with medium date and short time style.
 * Example output: "12 Oct 2026, 1:00 am"
 * 
 * @param {string|Date} isoString - ISO-8601 date string or Date object
 * @returns {string} Formatted local datetime string
 */
export const formatDateTime = (isoString) => {
  if (!isoString) return '';
  const date = typeof isoString === 'string' ? new Date(isoString) : isoString;
  if (isNaN(date.getTime())) return '';
  return date.toLocaleString('en-IN', {
    dateStyle: 'medium',
    timeStyle: 'short',
  });
};

/**
 * Converts a Date object or ISO string to local 'YYYY-MM-DDTHH:mm' string
 * suitable for HTML <input type="datetime-local" /> in the user's local timezone.
 * 
 * @param {Date|string} date - Date object or ISO string (defaults to now)
 * @returns {string} Formatted local input string 'YYYY-MM-DDTHH:mm'
 */
export const toLocalDatetimeInput = (date = new Date()) => {
  const d = typeof date === 'string' ? new Date(date) : date;
  if (isNaN(d.getTime())) return '';
  const pad = (n) => String(n).padStart(2, '0');
  const year = d.getFullYear();
  const month = pad(d.getMonth() + 1);
  const day = pad(d.getDate());
  const hours = pad(d.getHours());
  const minutes = pad(d.getMinutes());
  return `${year}-${month}-${day}T${hours}:${minutes}`;
};

/**
 * Converts a datetime-local input value (e.g. '2026-10-12T01:00') into a UTC ISO string.
 * Browsers construct `new Date('YYYY-MM-DDTHH:mm')` in the user's local timezone,
 * and `.toISOString()` converts it to standard UTC format.
 * 
 * @param {string} localValue - Value from datetime-local input
 * @returns {string|null} UTC ISO-8601 string (e.g. '2026-10-11T19:30:00.000Z')
 */
export const localInputToUtcIso = (localValue) => {
  if (!localValue) return null;
  const d = new Date(localValue);
  if (isNaN(d.getTime())) return null;
  return d.toISOString();
};
