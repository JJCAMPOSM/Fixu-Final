import React, { useCallback, useEffect, useState } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';
import { listMaintenance } from '../api';
import { colors, radius, STATUS_STYLE } from '../theme';
import Badge from '../components/Badge';

function formatDate(isoDate) {
  return new Date(`${isoDate}T00:00:00`).toLocaleDateString('es-MX', { weekday: 'short', day: 'numeric', month: 'short' });
}

export default function MaintenanceCalendarScreen({ navigation }) {
  const { token } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [error, setError] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    try {
      const data = await listMaintenance(token);
      setTasks(data);
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
      {!!error && <Text style={styles.error}>{error}</Text>}
      <FlatList
        data={tasks}
        keyExtractor={(item) => String(item.id)}
        onRefresh={onRefresh}
        refreshing={refreshing}
        contentContainerStyle={{ padding: 16 }}
        ListEmptyComponent={<Text style={styles.empty}>No tienes mantenimientos programados.</Text>}
        renderItem={({ item }) => {
          const status = STATUS_STYLE[item.status] || STATUS_STYLE.pending;
          const doneCount = item.checklist.filter((c) => c.is_done).length;
          return (
            <TouchableOpacity style={styles.card} onPress={() => navigation.navigate('Checklist', { taskId: item.id })} activeOpacity={0.8}>
              <View style={styles.dateBox}>
                <Text style={styles.dateText}>{formatDate(item.scheduled_date)}</Text>
              </View>
              <View style={{ flex: 1 }}>
                <Text style={styles.title} numberOfLines={1}>{item.title}</Text>
                {!!item.location && <Text style={styles.location}>📍 {item.location}</Text>}
                <View style={styles.badgeRow}>
                  <Badge label={status.label} bg={status.bg} fg={status.fg} />
                  <Text style={styles.progress}>{doneCount}/{item.checklist.length} items</Text>
                </View>
              </View>
              <Ionicons name="chevron-forward" size={20} color={colors.textMuted} />
            </TouchableOpacity>
          );
        }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.pageBg },
  error: { color: colors.danger, padding: 16 },
  empty: { color: colors.textMuted, textAlign: 'center', marginTop: 40 },
  card: {
    flexDirection: 'row', alignItems: 'center', backgroundColor: colors.white, borderRadius: radius.md,
    padding: 12, marginBottom: 10,
  },
  dateBox: { backgroundColor: colors.accentBg, borderRadius: radius.sm, padding: 8, marginRight: 12, minWidth: 74, alignItems: 'center' },
  dateText: { fontSize: 11, fontWeight: '700', color: colors.accent, textTransform: 'capitalize' },
  title: { fontSize: 15, fontWeight: '600', color: colors.textPrimary },
  location: { fontSize: 12, color: colors.textMuted, marginTop: 2 },
  badgeRow: { flexDirection: 'row', alignItems: 'center', gap: 8, marginTop: 6 },
  progress: { fontSize: 12, color: colors.textMuted },
});
