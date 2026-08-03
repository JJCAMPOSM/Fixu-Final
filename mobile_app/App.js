import React from 'react';
import { View, ActivityIndicator, StatusBar } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

import { AuthProvider, useAuth } from './src/context/AuthContext';
import LoginScreen from './src/screens/LoginScreen';
import RegisterScreen from './src/screens/RegisterScreen';
import ForgotPasswordScreen from './src/screens/ForgotPasswordScreen';
import HomeScreen from './src/screens/HomeScreen';
import TicketsScreen from './src/screens/TicketsScreen';
import NewTicketScreen from './src/screens/NewTicketScreen';
import TicketDetailScreen from './src/screens/TicketDetailScreen';
import EvaluateAttentionScreen from './src/screens/EvaluateAttentionScreen';
import NotificationsScreen from './src/screens/NotificationsScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import SettingsScreen from './src/screens/SettingsScreen';
import ChangePasswordScreen from './src/screens/ChangePasswordScreen';
import MaintenanceCalendarScreen from './src/screens/MaintenanceCalendarScreen';
import ChecklistScreen from './src/screens/ChecklistScreen';
import { colors } from './src/theme';

const Stack = createNativeStackNavigator();

const screenOptions = {
  headerStyle: { backgroundColor: colors.white },
  headerTintColor: colors.textPrimary,
  headerTitleStyle: { fontWeight: '700' },
};

function AuthStack() {
  return (
    <Stack.Navigator screenOptions={{ ...screenOptions, headerShown: false }}>
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen name="Register" component={RegisterScreen} options={{ headerShown: true, title: 'Crear cuenta' }} />
      <Stack.Screen name="ForgotPassword" component={ForgotPasswordScreen} options={{ headerShown: true, title: 'Recuperar contraseña' }} />
    </Stack.Navigator>
  );
}

function AppStack() {
  return (
    <Stack.Navigator screenOptions={screenOptions}>
      <Stack.Screen name="Home" component={HomeScreen} options={{ headerShown: false }} />
      <Stack.Screen name="Tickets" component={TicketsScreen} options={{ headerShown: false }} />
      <Stack.Screen name="NewTicket" component={NewTicketScreen} options={{ title: 'Nuevo reporte' }} />
      <Stack.Screen name="TicketDetail" component={TicketDetailScreen} options={{ title: 'Detalle del reporte' }} />
      <Stack.Screen name="EvaluateAttention" component={EvaluateAttentionScreen} options={{ title: 'Evaluar atención' }} />
      <Stack.Screen name="Notifications" component={NotificationsScreen} options={{ title: 'Notificaciones' }} />
      <Stack.Screen name="Profile" component={ProfileScreen} options={{ title: 'Perfil' }} />
      <Stack.Screen name="Settings" component={SettingsScreen} options={{ title: 'Configuración' }} />
      <Stack.Screen name="ChangePassword" component={ChangePasswordScreen} options={{ title: 'Cambiar contraseña' }} />
      <Stack.Screen name="MaintenanceCalendar" component={MaintenanceCalendarScreen} options={{ title: 'Calendario de mantenimientos' }} />
      <Stack.Screen name="Checklist" component={ChecklistScreen} options={{ title: 'Checklist' }} />
    </Stack.Navigator>
  );
}

function RootNavigator() {
  const { booting, token } = useAuth();

  if (booting) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: colors.pageBg }}>
        <ActivityIndicator color={colors.accent} size="large" />
      </View>
    );
  }

  return (
    <NavigationContainer>
      {token ? <AppStack /> : <AuthStack />}
    </NavigationContainer>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <StatusBar barStyle="dark-content" backgroundColor={colors.pageBg} />
      <RootNavigator />
    </AuthProvider>
  );
}
