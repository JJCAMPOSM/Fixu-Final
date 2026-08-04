import React from 'react';
import { Text, View, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';
import { colors, typography, radius } from '../theme';
import Screen from '../components/Screen';
import Card from '../components/Card';

export default function HomeScreen({ navigation }) {
  const { user } = useAuth();
  const isAgent = user?.role === 'agent';

  return (
    <Screen>
      <Text style={[typography.pageTitle, { marginBottom: 4 }]}>Hola, {user?.name?.split(' ')[0] || ''} 👋</Text>
      <Text style={styles.subtitle}>
        {isAgent ? 'Tu resumen de campo del día' : '¿Qué necesitas hacer hoy?'}
      </Text>

      {isAgent ? (
        <TouchableOpacity activeOpacity={0.8} onPress={() => navigation.navigate('MaintenanceCalendar')}>
          <Card style={styles.actionCard}>
            <Ionicons name="calendar-outline" size={26} color={colors.accent} />
            <Text style={styles.actionLabel}>Ver mantenimientos</Text>
          </Card>
        </TouchableOpacity>
      ) : (
        <TouchableOpacity activeOpacity={0.8} onPress={() => navigation.navigate('NewTicket')}>
          <Card style={styles.actionCard}>
            <Ionicons name="add-circle-outline" size={26} color={colors.accent} />
            <Text style={styles.actionLabel}>Nuevo reporte</Text>
          </Card>
        </TouchableOpacity>
      )}

      <Text style={styles.hint}>
        Usa la barra de abajo para ver tus reportes, notificaciones y tu perfil.
      </Text>
    </Screen>
  );
}

const styles = StyleSheet.create({
  subtitle: { ...typography.body, color: colors.textSecondary, marginBottom: 20 },
  actionCard: { alignItems: 'center', paddingVertical: 22, borderRadius: radius.md },
  actionLabel: { marginTop: 8, fontSize: 13, fontWeight: '600', color: colors.textPrimary, textAlign: 'center' },
  hint: { ...typography.label, color: colors.textMuted, textAlign: 'center', marginTop: 20 },
});
