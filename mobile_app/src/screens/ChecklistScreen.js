import React, { useCallback, useEffect, useState } from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';
import { getMaintenanceDetail, toggleChecklistItem } from '../api';
import { colors, radius, typography, STATUS_STYLE } from '../theme';
import Screen from '../components/Screen';
import Card from '../components/Card';
import Badge from '../components/Badge';

export default function ChecklistScreen({ route }) {
  const { token } = useAuth();
  const { taskId } = route.params;
  const [task, setTask] = useState(null);
  const [error, setError] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    try {
      const data = await getMaintenanceDetail(token, taskId);
      setTask(data);
      setError('');
    } catch (e) {
      setError(e.message);
    }
  }, [token, taskId]);

  useEffect(() => { load(); }, [load]);

  const onToggle = async (itemId) => {
    try {
      const data = await toggleChecklistItem(token, taskId, itemId);
      setTask(data);
    } catch (e) {
      setError(e.message);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  };

  if (!task) {
    return (
      <Screen>
        {!!error && <Text style={styles.error}>{error}</Text>}
      </Screen>
    );
  }

  const status = STATUS_STYLE[task.status] || STATUS_STYLE.pending;

  return (
    <Screen refreshing={refreshing} onRefresh={onRefresh}>
      <Text style={[typography.pageTitle, { fontSize: 20 }]}>{task.title}</Text>
      {!!task.location && <Text style={styles.location}>📍 {task.location}</Text>}
      <View style={{ marginTop: 8, marginBottom: 16 }}>
        <Badge label={status.label} bg={status.bg} fg={status.fg} />
      </View>

      {!!task.description && (
        <Card style={{ marginBottom: 16 }}>
          <Text style={styles.cardLabel}>Descripción</Text>
          <Text style={styles.cardBody}>{task.description}</Text>
        </Card>
      )}

      <Text style={typography.sectionHeader}>Checklist</Text>
      {task.checklist.map((item) => (
        <Pressable key={item.id} style={styles.item} onPress={() => onToggle(item.id)}>
          <Ionicons
            name={item.is_done ? 'checkbox' : 'square-outline'}
            size={22}
            color={item.is_done ? colors.success : colors.textMuted}
          />
          <Text style={[styles.itemText, item.is_done && styles.itemTextDone]}>{item.description}</Text>
        </Pressable>
      ))}

      {!!error && <Text style={styles.error}>{error}</Text>}
    </Screen>
  );
}

const styles = StyleSheet.create({
  location: { fontSize: 13, color: colors.textMuted, marginTop: 4 },
  cardLabel: { fontSize: 12, color: colors.textMuted, marginBottom: 4, fontWeight: '600' },
  cardBody: { fontSize: 14, color: colors.textPrimary, lineHeight: 20 },
  item: {
    flexDirection: 'row', alignItems: 'center', backgroundColor: colors.white, borderRadius: radius.md,
    padding: 14, marginTop: 8, gap: 10,
  },
  itemText: { flex: 1, fontSize: 14, color: colors.textPrimary },
  itemTextDone: { color: colors.textMuted, textDecorationLine: 'line-through' },
  error: { color: colors.danger, marginTop: 14 },
});
