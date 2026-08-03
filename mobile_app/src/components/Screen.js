import React from 'react';
import { ScrollView, View, StyleSheet, RefreshControl } from 'react-native';
import { colors } from '../theme';

export default function Screen({ children, scroll = true, padded = true, refreshing, onRefresh }) {
  if (!scroll) {
    return <View style={[styles.wrap, padded && styles.padded]}>{children}</View>;
  }
  return (
    <ScrollView
      style={styles.wrap}
      contentContainerStyle={[padded && styles.padded, styles.grow]}
      refreshControl={onRefresh ? <RefreshControl refreshing={!!refreshing} onRefresh={onRefresh} /> : undefined}
    >
      {children}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: colors.pageBg },
  padded: { padding: 16 },
  grow: { flexGrow: 1 },
});
