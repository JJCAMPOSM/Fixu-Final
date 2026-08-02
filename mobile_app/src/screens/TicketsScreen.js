import React, { useCallback, useEffect, useState } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet, RefreshControl, Image } from 'react-native';
import { listTickets } from '../api';

const STATUS_LABEL = { open: 'Abierto', pending: 'Pendiente', solved: 'Resuelto', closed: 'Cerrado' };

export default function TicketsScreen({ token, user, onNewTicket, onLogout }) {
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

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View>
          <Text style={styles.headerTitle}>Mis tickets</Text>
          <Text style={styles.headerSubtitle}>{user?.name}</Text>
        </View>
        <TouchableOpacity onPress={onLogout}>
          <Text style={styles.logout}>Salir</Text>
        </TouchableOpacity>
      </View>

      {!!error && <Text style={styles.error}>{error}</Text>}

      <FlatList
        data={tickets}
        keyExtractor={(item) => String(item.id)}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        contentContainerStyle={{ padding: 16 }}
        ListEmptyComponent={<Text style={styles.empty}>Aún no has creado tickets desde el campo.</Text>}
        renderItem={({ item }) => (
          <View style={styles.card}>
            {item.photo_url ? (
              <Image source={{ uri: item.photo_url }} style={styles.thumb} />
            ) : (
              <View style={[styles.thumb, styles.thumbPlaceholder]} />
            )}
            <View style={{ flex: 1 }}>
              <Text style={styles.cardTitle}>{item.title}</Text>
              <Text style={styles.cardStatus}>{STATUS_LABEL[item.status] || item.status} · {item.priority}</Text>
            </View>
          </View>
        )}
      />

      <TouchableOpacity style={styles.fab} onPress={onNewTicket}>
        <Text style={styles.fabText}>+ Nuevo ticket</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#111827' },
  header: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    padding: 16, paddingTop: 48,
  },
  headerTitle: { color: '#fff', fontSize: 22, fontWeight: '700' },
  headerSubtitle: { color: '#9ca3af', fontSize: 13 },
  logout: { color: '#f87171', fontWeight: '600' },
  error: { color: '#f87171', paddingHorizontal: 16 },
  empty: { color: '#9ca3af', textAlign: 'center', marginTop: 40 },
  card: {
    flexDirection: 'row', backgroundColor: '#1f2937', borderRadius: 12,
    padding: 12, marginBottom: 10, alignItems: 'center', gap: 12,
  },
  thumb: { width: 52, height: 52, borderRadius: 8, marginRight: 12, backgroundColor: '#374151' },
  thumbPlaceholder: {},
  cardTitle: { color: '#fff', fontSize: 15, fontWeight: '600' },
  cardStatus: { color: '#9ca3af', fontSize: 12, marginTop: 2 },
  fab: {
    position: 'absolute', bottom: 24, right: 24, backgroundColor: '#4f46e5',
    borderRadius: 30, paddingVertical: 14, paddingHorizontal: 20,
  },
  fabText: { color: '#fff', fontWeight: '700' },
});
