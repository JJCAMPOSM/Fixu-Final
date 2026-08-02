import React, { useEffect, useState } from 'react';
import { View, ActivityIndicator, StatusBar } from 'react-native';
import * as SecureStore from 'expo-secure-store';

import LoginScreen from './src/screens/LoginScreen';
import TicketsScreen from './src/screens/TicketsScreen';
import NewTicketScreen from './src/screens/NewTicketScreen';

export default function App() {
  const [booting, setBooting] = useState(true);
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  const [screen, setScreen] = useState('tickets'); // 'tickets' | 'new'

  useEffect(() => {
    (async () => {
      const savedToken = await SecureStore.getItemAsync('fixu_token');
      const savedUser = await SecureStore.getItemAsync('fixu_user');
      if (savedToken && savedUser) {
        setToken(savedToken);
        setUser(JSON.parse(savedUser));
      }
      setBooting(false);
    })();
  }, []);

  const handleLoggedIn = async (newToken, newUser) => {
    await SecureStore.setItemAsync('fixu_token', newToken);
    await SecureStore.setItemAsync('fixu_user', JSON.stringify(newUser));
    setToken(newToken);
    setUser(newUser);
  };

  const handleLogout = async () => {
    await SecureStore.deleteItemAsync('fixu_token');
    await SecureStore.deleteItemAsync('fixu_user');
    setToken(null);
    setUser(null);
    setScreen('tickets');
  };

  if (booting) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#111827' }}>
        <ActivityIndicator color="#4f46e5" size="large" />
      </View>
    );
  }

  return (
    <View style={{ flex: 1 }}>
      <StatusBar barStyle="light-content" backgroundColor="#111827" />
      {!token ? (
        <LoginScreen onLoggedIn={handleLoggedIn} />
      ) : screen === 'new' ? (
        <NewTicketScreen
          token={token}
          onCreated={() => setScreen('tickets')}
          onCancel={() => setScreen('tickets')}
        />
      ) : (
        <TicketsScreen
          token={token}
          user={user}
          onNewTicket={() => setScreen('new')}
          onLogout={handleLogout}
        />
      )}
    </View>
  );
}
