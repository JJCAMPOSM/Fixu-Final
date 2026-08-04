import React from 'react';
import { ScrollView, View, StyleSheet, RefreshControl } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors } from '../theme';

export default function Screen({ children, scroll = true, padded = true, refreshing, onRefresh }) {
  if (!scroll) {
    return (
      <SafeAreaView style={[styles.wrap, padded && styles.padded]} edges={['top']}>
        {children}
      </SafeAreaView>
    );
  }
  return (
    <SafeAreaView style={styles.wrap} edges={['top']}>
      <ScrollView
        contentContainerStyle={[padded && styles.padded, styles.grow]}
        refreshControl={onRefresh ? <RefreshControl refreshing={!!refreshing} onRefresh={onRefresh} /> : undefined}
      >
        {children}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: colors.pageBg },
  padded: { padding: 16 },
  grow: { flexGrow: 1 },
});
