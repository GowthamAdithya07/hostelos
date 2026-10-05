// Category detection & visual styling helper matching document UI specs

export const detectCategory = (title = '', description = '') => {
  const text = `${title} ${description}`.toLowerCase();
  if (/laptop|phone|mobile|charger|headphone|earbud|airpod|ipad|tablet|watch|cable|dell|macbook|iphone|samsung/.test(text)) {
    return 'Electronics';
  }
  if (/card|id|license|passport|aadhaar|pan|hall ticket|pass|identity/.test(text)) {
    return 'ID & Cards';
  }
  if (/key|keys|keychain|fob/.test(text)) {
    return 'Keys';
  }
  if (/bag|backpack|wallet|purse|pouch|suitcase/.test(text)) {
    return 'Bags & Wallets';
  }
  if (/book|notebook|journal|notes|binder|pen|pencil/.test(text)) {
    return 'Books & Notes';
  }
  if (/jacket|coat|hoodie|umbrella|bottle|flask|shoe|glasses|specs/.test(text)) {
    return 'Accessories';
  }
  return 'General';
};

export const getCategoryBadgeStyle = (category) => {
  switch (category) {
    case 'Electronics':
      return 'bg-purple-100 text-purple-700 border-purple-200';
    case 'ID & Cards':
      return 'bg-blue-100 text-blue-700 border-blue-200';
    case 'Keys':
      return 'bg-amber-100 text-amber-800 border-amber-200';
    case 'Bags & Wallets':
      return 'bg-cyan-100 text-cyan-800 border-cyan-200';
    case 'Books & Notes':
      return 'bg-emerald-100 text-emerald-800 border-emerald-200';
    case 'Accessories':
      return 'bg-pink-100 text-pink-800 border-pink-200';
    default:
      return 'bg-slate-100 text-slate-700 border-slate-200';
  }
};

export const formatItemReferenceId = (id) => {
  return `RE-2026-${String(id).padStart(4, '0')}`;
};

export const getUrgency = (item) => {
  const text = `${item.title} ${item.description}`.toLowerCase();
  if (item.type === 'LOST') {
    if (/laptop|phone|macbook|wallet|passport|id card|keys/.test(text)) {
      return { label: 'High', style: 'bg-rose-100 text-rose-700' };
    }
    return { label: 'Medium', style: 'bg-amber-100 text-amber-700' };
  }
  return { label: 'Low', style: 'bg-slate-100 text-slate-600' };
};
