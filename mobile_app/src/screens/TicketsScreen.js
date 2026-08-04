import React, { useCallback, useEffect, useState } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet, Image } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { listTickets, withAuthToken } from '../api';
import { colors, typography, radius, STATUS_STYLE, PRIORITY_STYLE } from '../theme';
import Badge from '../components/Badge';
import { useAuth } from '../context/AuthContext';

export default function TicketsScreen({ navigation }) {
  const { token, user } = useAuth();
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

  const activeCount = tickets.filter((t) => !['resolved', 'cancelled'].includes(t.status)).length;

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <Text style={[typography.pageTitle, { fontSize: 20 }]}>Hola, {user?.name?.split(' ')[0] || 'Agente'}</Text>
        <Text style={styles.headerSubtitle}>{activeCount} reporte(s) activos</Text>
      </View>

      {!!error && <Text style={styles.error}>{error}</Text>}

      <FlatList
        data={tickets}
        keyExtractor={(item) => String(item.id)}
        onRefresh={onRefresh}
        refreshing={refreshing}
        contentContainerStyle={{ padding: 16, paddingBottom: 100 }}
        ListEmptyComponent={
          <Text style={styles.empty}>
            {user?.role === 'agent' ? 'No tenés tickets asignados por el momento.' : 'Aún no has creado reportes desde el campo.'}
          </Text>
        }
        renderItem={({ item }) => {
          const status = STATUS_STYLE[item.status] || STATUS_STYLE.pending;
          const priority = PRIORITY_STYLE[item.priority] || PRIORITY_STYLE.medium;
          return (
            <TouchableOpacity style={styles.card} onPress={() => navigation.navigate('TicketDetail', { ticket: item })} activeOpacity={0.8}>
              {item.photo_url ? (
                <Image source={{ uri: withAuthToken(item.photo_url, token) }} style={styles.thumb} />
              ) : (
                <View style={[styles.thumb, styles.thumbPlaceholder]}>
                  <Ionicons name="document-text-outline" size={22} color={colors.textMuted} />
                </View>
              )}
              <View style={{ flex: 1 }}>
                <Text style={styles.cardTitle} numberOfLines={1}>{item.title}</Text>
                {(item.building || item.classroom) && (
                  <Text style={styles.cardSubtitle} numberOfLines={1}>
                    {[item.building, item.classroom].filter(Boolean).join(' · ')}
                  </Text>
                )}
                <View style={styles.badgeRow}>
                  <Badge label={status.label} bg={status.bg} fg={status.fg} />
                  <Badge label={priority.label} bg={priority.bg} fg={priority.fg} />
                </View>
              </View>
              <Ionicons name="chevron-forward" size={20} color={colors.textMuted} />
            </TouchableOpacity>
          );
        }}
      />

      {user?.role !== 'agent' && (
        <TouchableOpacity style={styles.fab} onPress={() => navigation.navigate('NewTicket')}>
          <Text style={styles.fabText}>+ Nuevo reporte</Text>
        </TouchableOpacity>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.pageBg },
  header: { padding: 16, paddingTop: 52 },
  headerSubtitle: { color: colors.textMuted, fontSize: 13, marginTop: 2 },
  error: { color: colors.danger, paddingHorizontal: 16 },
  empty: { color: colors.textMuted, textAlign: 'center', marginTop: 40 },
  card: {
    flexDirection: 'row', backgroundColor: colors.white, borderRadius: radius.md,
    padding: 12, marginBottom: 10, alignItems: 'center',
    shadowColor: '#000', shadowOpacity: 0.04, shadowRadius: 6, shadowOffset: { width: 0, height: 2 }, elevation: 1,
  },
  thumb: { width: 52, height: 52, borderRadius: 10, marginRight: 12, backgroundColor: colors.pageBg },
  thumbPlaceholder: { justifyContent: 'center', alignItems: 'center' },
  cardTitle: { color: colors.textPrimary, fontSize: 15, fontWeight: '600' },
  cardSubtitle: { color: colors.textMuted, fontSize: 12, marginTop: 2 },
  badgeRow: { flexDirection: 'row', gap: 6, marginTop: 6 },
  fab: {
    position: 'absolute', bottom: 24, right: 24, backgroundColor: colors.accent,
    borderRadius: radius.pill, paddingVertical: 14, paddingHorizontal: 20,
    shadowColor: '#000', shadowOpacity: 0.2, shadowRadius: 8, shadowOffset: { width: 0, height: 4 }, elevation: 4,
  },
  fabText: { color: colors.white, fontWeight: '700' },
});
