import React from 'react';
import { Text, View, StyleSheet, Image } from 'react-native';
import { colors, typography, radius } from '../theme';
import Screen from '../components/Screen';

export default function AboutScreen() {
  return (
    <Screen>
      <View style={styles.header}>
        <Image source={require('../../assets/logo.png')} style={styles.logo} resizeMode="contain" />
        <Text style={[typography.pageTitle, { fontSize: 20, marginTop: 10 }]}>Fixu</Text>
        <Text style={styles.version}>Versión 1.0.0</Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.body}>
          Fixu es la herramienta de campo para reportar y darle seguimiento a fallas de equipo
          desde el sitio, con evidencia fotográfica. Conecta a solicitantes y agentes de soporte
          en un mismo flujo, desde el reporte inicial hasta la resolución.
        </Text>
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  header: { alignItems: 'center', marginBottom: 20 },
  logo: { width: 72, height: 72 },
  version: { color: colors.textMuted, fontSize: 13, marginTop: 2 },
  card: { backgroundColor: colors.white, borderRadius: radius.md, padding: 16 },
  body: { fontSize: 14, color: colors.textPrimary, lineHeight: 21 },
});
