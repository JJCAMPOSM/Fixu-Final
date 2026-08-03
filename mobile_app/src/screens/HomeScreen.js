import React from 'react';
import { Text, View, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';
import { colors, typography, radius } from '../theme';
import Screen from '../components/Screen';
import Card from '../components/Card';

function ActionCard({ icon, label, onPress }) {
  return (
    <TouchableOpacity onPress={onPress} activeOpacity={0.8} style={{ width: '48%', marginBottom: 12 }}>
      <Card style={styles.actionCard}>
        <Ionicons name={icon} size={26} color={colors.accent} />
        <Text style={styles.actionLabel}>{label}</Text>
      </Card>
    </TouchableOpacity>
  );
}

export default function HomeScreen({ navigation }) {
  const { user } = useAuth();
  const isAgent = user?.role === 'agent';

  return (
    <Screen>
      <Text style={[typography.pageTitle, { marginBottom: 4 }]}>Hola, {user?.name?.split(' ')[0] || ''} 👋</Text>
      <Text style={styles.subtitle}>
        {isAgent ? 'Tu resumen de campo del día' : '¿Qué necesitas hacer hoy?'}
      </Text>

      <View style={styles.grid}>
        {!isAgent && <ActionCard icon="add-circle-outline" label="Nuevo reporte" onPress={() => navigation.navigate('NewTicket')} />}
        <ActionCard icon="list-outline" label="Mis reportes" onPress={() => navigation.navigate('Tickets')} />
        {isAgent && <ActionCard icon="calendar-outline" label="Mantenimientos" onPress={() => navigation.navigate('MaintenanceCalendar')} />}
        <ActionCard icon="notifications-outline" label="Notificaciones" onPress={() => navigation.navigate('Notifications')} />
        <ActionCard icon="person-outline" label="Perfil" onPress={() => navigation.navigate('Profile')} />
        <ActionCard icon="settings-outline" label="Configuración" onPress={() => navigation.navigate('Settings')} />
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  subtitle: { ...typography.body, color: colors.textSecondary, marginBottom: 20 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between' },
  actionCard: { alignItems: 'center', paddingVertical: 22, borderRadius: radius.md },
  actionLabel: { marginTop: 8, fontSize: 13, fontWeight: '600', color: colors.textPrimary, textAlign: 'center' },
});
