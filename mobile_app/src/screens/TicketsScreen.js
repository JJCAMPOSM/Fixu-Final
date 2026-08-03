import React, { useCallback, useEffect, useState } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet, RefreshControl, Image } from 'react-native';
import { listTickets } from '../api';
import { colors, STATUS_STYLE, PRIORITY_STYLE } from '../theme';
import FieldModeBadge from '../components/FieldModeBadge';
import { useAuth } from '../context/AuthContext';

export default function TicketsScreen({ navigation }) {
  const { token, user, logout } = useAuth();
  const [tickets, setTickets] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    try {
      const data = await listTickets(token);
      setTickets(data);
      setError('');
    } catch (e) {
      setError(e.message);
    }
  }, [token]);

  useEffect(() => { load(); }, [load]);

  const onRefresh = async () => {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  };

  const activeCount = tickets.filter((t) => t.status !== 'closed').length;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <FieldModeBadge />
        <View style={styles.headerRow}>
          <View>
            <Text style={styles.headerTitle}>Hola, {user?.name?.split(' ')[0] || 'Agente'} 👋</Text>
            <Text style={styles.headerSubtitle}>{activeCount} ticket(s) activos</Text>
          </View>
          <TouchableOpacity onPress={logout}>
            <Text style={styles.logout}>Salir</Text>
          </TouchableOpacity>
        </View>
      </View>

      {!!error && <Text style={styles.error}>{error}</Text>}

      <FlatList
        data={tickets}
        keyExtractor={(item) => String(item.id)}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        contentContainerStyle={{ padding: 16, paddingBottom: 100 }}
        ListEmptyComponent={<Text style={styles.empty}>Aún no has creado tickets desde el campo.</Text>}
        renderItem={({ item }) => {
          const status = STATUS_STYLE[item.status] || STATUS_STYLE.open;
          const priority = PRIORITY_STYLE[item.priority] || PRIORITY_STYLE.medium;
          return (
            <TouchableOpacity style={styles.card} onPress={() => navigation.navigate('TicketDetail', { ticket: item })} activeOpacity={0.8}>
              {item.photo_url ? (
                <Image
                  source={{ uri: item.photo_url, headers: { Authorization: `Bearer ${token}` } }}
                  style={styles.thumb}
                />
              ) : (
                <View style={[styles.thumb, styles.thumbPlaceholder]}>
                  <Text style={{ fontSize: 18 }}>📋</Text>
                </View>
              )}
              <View style={{ flex: 1 }}>
                <Text style={styles.cardTitle} numberOfLines={1}>{item.title}</Text>
                <View style={styles.badgeRow}>
                  <View style={[styles.badge, { backgroundColor: status.bg }]}>
                    <Text style={[styles.badgeText, { color: status.fg }]}>{status.label}</Text>
                  </View>
                  <View style={[styles.badge, { backgroundColor: priority.bg }]}>
                    <Text style={[styles.badgeText, { color: priority.fg }]}>{priority.label}</Text>
                  </View>
                </View>
              </View>
              <Text style={styles.chevron}>›</Text>
            </TouchableOpacity>
          );
        }}
      />

      <TouchableOpacity style={styles.fab} onPress={() => navigation.navigate('NewTicket')}>
        <Text style={styles.fabText}>+ Nuevo ticket</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  header: { padding: 16, paddingTop: 52 },
  headerRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  headerTitle: { color: colors.text, fontSize: 22, fontWeight: '700' },
  headerSubtitle: { color: colors.textMuted, fontSize: 13, marginTop: 2 },
  logout: { color: colors.danger, fontWeight: '600' },
  error: { color: colors.danger, paddingHorizontal: 16 },
  empty: { color: colors.textMuted, textAlign: 'center', marginTop: 40 },
  card: {
    flexDirection: 'row', backgroundColor: colors.surface, borderRadius: 14,
    padding: 12, marginBottom: 10, alignItems: 'center',
    shadowColor: '#000', shadowOpacity: 0.04, shadowRadius: 6, shadowOffset: { width: 0, height: 2 }, elevation: 1,
  },
  thumb: { width: 52, height: 52, borderRadius: 10, marginRight: 12, backgroundColor: colors.background },
  thumbPlaceholder: { justifyContent: 'center', alignItems: 'center' },
  cardTitle: { color: colors.text, fontSize: 15, fontWeight: '600' },
  badgeRow: { flexDirection: 'row', gap: 6, marginTop: 6 },
  badge: { borderRadius: 20, paddingVertical: 3, paddingHorizontal: 9, marginRight: 6 },
  badgeText: { fontSize: 11, fontWeight: '700' },
  chevron: { color: colors.textMuted, fontSize: 22, marginLeft: 6 },
  fab: {
    position: 'absolute', bottom: 24, right: 24, backgroundColor: colors.primary,
    borderRadius: 30, paddingVertical: 14, paddingHorizontal: 20,
    shadowColor: '#000', shadowOpacity: 0.2, shadowRadius: 8, shadowOffset: { width: 0, height: 4 }, elevation: 4,
  },
  fabText: { color: '#fff', fontWeight: '700' },
});
