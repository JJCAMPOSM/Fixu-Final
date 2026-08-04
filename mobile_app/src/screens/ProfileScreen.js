import React, { useEffect, useState } from 'react';
import { Text, View, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';
import { listTickets } from '../api';
import { colors, typography, radius } from '../theme';
import Screen from '../components/Screen';
import Card from '../components/Card';
import Badge from '../components/Badge';

const ROLE_LABEL = { agent: 'Agente', requester: 'Solicitante', admin: 'Administrador' };

const DONE_STATUSES = ['resolved', 'cancelled'];

function formatDuration(ms) {
  const hours = ms / (1000 * 60 * 60);
  if (hours < 1) return `${Math.max(1, Math.round(ms / (1000 * 60)))} min`;
  if (hours < 24) return `${hours.toFixed(1)} h`;
  return `${(hours / 24).toFixed(1)} días`;
}

function useAgentStats(token, enabled) {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    if (!enabled) return;
    let cancelled = false;
    listTickets(token)
      .then((tickets) => {
        if (cancelled) return;
        const atendidos = tickets.filter((t) => t.status === 'resolved').length;
        const pendientes = tickets.filter((t) => !DONE_STATUSES.includes(t.status)).length;
        const resolved = tickets.filter((t) => t.status === 'resolved' && t.resolved_at);
        let avgLabel = '—';
        if (resolved.length) {
          const totalMs = resolved.reduce(
            (sum, t) => sum + (new Date(t.resolved_at).getTime() - new Date(t.created_at).getTime()),
            0,
          );
          avgLabel = formatDuration(totalMs / resolved.length);
        }
        setStats({ atendidos, pendientes, avgLabel });
      })
      .catch(() => setStats(null));
    return () => { cancelled = true; };
  }, [token, enabled]);

  return stats;
}

export default function ProfileScreen({ navigation }) {
  const { user, token, logout } = useAuth();
  const isAgent = user?.role === 'agent';
  const stats = useAgentStats(token, isAgent);

  return (
    <Screen>
      <View style={styles.avatarWrap}>
        <View style={styles.avatar}>
          <Ionicons name="person" size={40} color={colors.white} />
        </View>
        <Text style={[typography.pageTitle, { fontSize: 20, marginTop: 10 }]}>{user?.name}</Text>
        <Badge label={ROLE_LABEL[user?.role] || user?.role} bg={colors.accentBg} fg={colors.accent} />
      </View>

      {isAgent ? (
        <Card style={{ marginTop: 20 }}>
          <Text style={styles.label}>Nombre completo</Text>
          <Text style={[styles.value, { marginBottom: 14 }]}>{user?.name}</Text>

          <Text style={styles.label}>Correo institucional</Text>
          <Text style={[styles.value, { marginBottom: 14 }]}>{user?.email}</Text>

          <Text style={styles.label}>Tickets atendidos</Text>
          <Text style={[styles.value, { marginBottom: 14 }]}>{stats ? stats.atendidos : '—'}</Text>

          <Text style={styles.label}>Tickets pendientes</Text>
          <Text style={[styles.value, { marginBottom: 14 }]}>{stats ? stats.pendientes : '—'}</Text>

          <Text style={styles.label}>Tiempo promedio de atención</Text>
          <Text style={styles.value}>{stats ? stats.avgLabel : '—'}</Text>
        </Card>
      ) : (
        <Card style={{ marginTop: 20 }}>
          <Text style={styles.label}>Correo</Text>
          <Text style={styles.value}>{user?.email}</Text>
        </Card>
      )}

      <TouchableOpacity style={styles.row} onPress={() => navigation.navigate('ChangePassword')}>
        <Ionicons name="key-outline" size={20} color={colors.textPrimary} />
        <Text style={styles.rowText}>Cambiar contraseña</Text>
        <Ionicons name="chevron-forward" size={18} color={colors.textMuted} />
      </TouchableOpacity>

      <TouchableOpacity style={styles.row} onPress={() => navigation.navigate('About')}>
        <Ionicons name="information-circle-outline" size={20} color={colors.textPrimary} />
        <Text style={styles.rowText}>Acerca de Fixu</Text>
        <Ionicons name="chevron-forward" size={18} color={colors.textMuted} />
      </TouchableOpacity>

      <TouchableOpacity style={styles.row} onPress={() => navigation.navigate('Terms')}>
        <Ionicons name="document-text-outline" size={20} color={colors.textPrimary} />
        <Text style={styles.rowText}>Términos y condiciones</Text>
        <Ionicons name="chevron-forward" size={18} color={colors.textMuted} />
      </TouchableOpacity>

      <TouchableOpacity style={[styles.row, { marginTop: 20 }]} onPress={logout}>
        <Ionicons name="log-out-outline" size={20} color={colors.danger} />
        <Text style={[styles.rowText, { color: colors.danger }]}>Cerrar sesión</Text>
      </TouchableOpacity>
    </Screen>
  );
}

const styles = StyleSheet.create({
  avatarWrap: { alignItems: 'center', marginBottom: 8 },
  avatar: { width: 80, height: 80, borderRadius: 40, backgroundColor: colors.accent, justifyContent: 'center', alignItems: 'center' },
  label: { fontSize: 12, color: colors.textMuted, marginBottom: 4, fontWeight: '600' },
  value: { fontSize: 15, color: colors.textPrimary },
  row: {
    flexDirection: 'row', alignItems: 'center', backgroundColor: colors.white, borderRadius: radius.md,
    padding: 14, marginTop: 10, gap: 10,
  },
  rowText: { flex: 1, fontSize: 14, fontWeight: '600', color: colors.textPrimary },
});
