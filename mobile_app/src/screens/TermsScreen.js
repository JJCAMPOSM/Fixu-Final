import React from 'react';
import { Text, StyleSheet } from 'react-native';
import { colors } from '../theme';
import Screen from '../components/Screen';

const SECTIONS = [
  {
    title: '1. Uso de la aplicación',
    body: 'Fixu está destinada a reportar y darle seguimiento a fallas de equipo dentro de la institución. El uso de la app implica aceptar reportar información veraz sobre las incidencias.',
  },
  {
    title: '2. Datos personales',
    body: 'La información de contacto (nombre, correo, teléfono) se usa únicamente para identificar al solicitante y darle seguimiento a sus reportes. No se comparte con terceros.',
  },
  {
    title: '3. Evidencia fotográfica',
    body: 'Las fotos adjuntas a un reporte son visibles solo para el solicitante que lo creó y para los agentes/administradores encargados de atenderlo.',
  },
  {
    title: '4. Responsabilidad',
    body: 'Fixu es una herramienta de gestión interna; no sustituye los canales oficiales de emergencia ni de seguridad de la institución.',
  },
];

export default function TermsScreen() {
  return (
    <Screen>
      {SECTIONS.map((s) => (
        <React.Fragment key={s.title}>
          <Text style={styles.sectionTitle}>{s.title}</Text>
          <Text style={styles.sectionBody}>{s.body}</Text>
        </React.Fragment>
      ))}
    </Screen>
  );
}

const styles = StyleSheet.create({
  sectionTitle: { fontSize: 14, fontWeight: '700', color: colors.textPrimary, marginTop: 16 },
  sectionBody: { fontSize: 13, color: colors.textSecondary, lineHeight: 20, marginTop: 6 },
});
