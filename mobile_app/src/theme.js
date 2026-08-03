// Paleta oficial de Fixu (guía de estilo). Se mantienen los alias antiguos
// (primary, background, surface, text, ...) para no romper las pantallas
// existentes; las nuevas pantallas usan los nombres de la guía directamente.
export const colors = {
  accent: '#6366F1',
  accentBg: '#EEEDFE',
  success: '#10B981',
  successBg: '#D1FAE5',
  warning: '#F59E0B',
  warningBg: '#FEF3C7',
  danger: '#EF4444',
  dangerBg: '#FEE2E2',
  neutral: '#9CA3AF',
  neutralBg: '#F3F4F6',
  pageBg: '#F3F4F6',
  white: '#FFFFFF',
  textPrimary: '#111827',
  textSecondary: '#6B7280',
  textMuted: '#9CA3AF',
  border: '#E5E7EB',
  info: '#2563EB',
  infoBg: '#DBEAFE',

  // Alias retrocompatibles usados por las pantallas ya existentes.
  primary: '#6366F1',
  primaryDark: '#4C4EDB',
  background: '#F3F4F6',
  surface: '#FFFFFF',
  text: '#111827',
};

export const typography = {
  pageTitle: { fontSize: 24, fontWeight: '600', color: colors.textPrimary },
  sectionHeader: {
    fontSize: 13, fontWeight: '700', color: colors.textSecondary,
    textTransform: 'uppercase', letterSpacing: 0.6,
  },
  body: { fontSize: 14, fontWeight: '400', color: colors.textPrimary },
  label: { fontSize: 13, fontWeight: '400', color: colors.textSecondary },
  placeholder: { fontSize: 14, fontStyle: 'italic', color: colors.textMuted },
  badge: { fontSize: 12, fontWeight: '700', textTransform: 'uppercase', letterSpacing: 0.4 },
};

export const radius = { sm: 8, md: 12, lg: 20, pill: 999 };
export const spacing = { xs: 4, sm: 8, md: 16, lg: 24, xl: 32 };

export const STATUS_STYLE = {
  pending: { label: 'Pendiente', bg: colors.warningBg, fg: colors.warning },
  assigned: { label: 'Asignado', bg: colors.infoBg, fg: colors.info },
  in_progress: { label: 'En proceso', bg: colors.accentBg, fg: colors.accent },
  on_hold: { label: 'En espera', bg: colors.warningBg, fg: colors.warning },
  cancelled: { label: 'Cancelado', bg: colors.dangerBg, fg: colors.danger },
  resolved: { label: 'Resuelto', bg: colors.successBg, fg: colors.success },
  done: { label: 'Completado', bg: colors.successBg, fg: colors.success },
};

export const PRIORITY_STYLE = {
  low: { label: 'Baja', bg: colors.successBg, fg: colors.success },
  medium: { label: 'Media', bg: colors.warningBg, fg: colors.warning },
  high: { label: 'Alta', bg: colors.dangerBg, fg: colors.danger },
};
