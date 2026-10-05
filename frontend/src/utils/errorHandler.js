/**
 * Extracts a human-readable string from any API error.
 * Handles FastAPI / Pydantic validation errors (array of {type, loc, msg, input, ctx}),
 * standard HTTP error strings, or generic Javascript Errors without ever returning an object.
 */
export const formatErrorMessage = (err, fallback = 'An unexpected error occurred. Please try again.') => {
  if (!err) return fallback;

  const detail = err.response?.data?.detail;
  if (!detail) {
    return err.message || fallback;
  }

  // If detail is a plain string
  if (typeof detail === 'string') {
    return detail;
  }

  // If detail is an array of Pydantic validation objects
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === 'string') return item;
        if (item && item.msg) {
          const field = Array.isArray(item.loc) ? item.loc[item.loc.length - 1] : '';
          return field ? `${field}: ${item.msg}` : item.msg;
        }
        return JSON.stringify(item);
      })
      .join(' | ');
  }

  // If detail is a single object
  if (typeof detail === 'object') {
    return detail.msg || detail.message || JSON.stringify(detail);
  }

  return String(detail);
};

export default formatErrorMessage;
