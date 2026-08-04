import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../theme';

import HomeScreen from '../screens/HomeScreen';
import TicketsScreen from '../screens/TicketsScreen';
import NotificationsScreen from '../screens/NotificationsScreen';
import ProfileScreen from '../screens/ProfileScreen';

const ICONS = {
  Home: 'home',
  Tickets: 'list',
  Notifications: 'notifications',
  Profile: 'person',
};

const TAB_LABELS = {
  Home: 'Inicio',
  Tickets: 'Reportes',
  Notifications: 'Notificaciones',
  Profile: 'Perfil',
};

const Tab = createBottomTabNavigator();

export default function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerStyle: { backgroundColor: colors.white },
        headerTintColor: colors.textPrimary,
        headerTitleStyle: { fontWeight: '700' },
        tabBarActiveTintColor: colors.accent,
        tabBarInactiveTintColor: colors.textMuted,
        tabBarLabel: TAB_LABELS[route.name],
        tabBarStyle: { backgroundColor: colors.white, borderTopColor: colors.border },
        tabBarIcon: ({ color, size, focused }) => (
          <Ionicons name={`${ICONS[route.name]}${focused ? '' : '-outline'}`} size={size} color={color} />
        ),
      })}
    >
      <Tab.Screen name="Home" component={HomeScreen} options={{ headerShown: false }} />
      <Tab.Screen name="Tickets" component={TicketsScreen} options={{ headerShown: false }} />
      <Tab.Screen name="Notifications" component={NotificationsScreen} options={{ title: 'Notificaciones' }} />
      <Tab.Screen name="Profile" component={ProfileScreen} options={{ title: 'Perfil' }} />
    </Tab.Navigator>
  );
}
