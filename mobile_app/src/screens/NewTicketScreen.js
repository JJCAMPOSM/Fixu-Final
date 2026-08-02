import React, { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet, Image, ActivityIndicator, ScrollView,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import * as Location from 'expo-location';
import { createTicket } from '../api';
import { colors, PRIORITY_STYLE } from '../theme';
import FieldModeBadge from '../components/FieldModeBadge';
import { useAuth } from '../context/AuthContext';

const PRIORITIES = ['low', 'medium', 'high'];

export default function NewTicketScreen({ navigation }) {
  const { token } = useAuth();
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  const [priority, setPriority] = useState('medium');
  const [photo, setPhoto] = useState(null); // { base64, uri }
  const [location, setLocation] = useState(null); // solo informativo, no se envía al servidor
  const [locationError, setLocationError] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const validate = () => {
    if (title.trim().length < 3) return 'El título debe tener al menos 3 caracteres.';
    if (title.length > 200) return 'El título es demasiado largo (máx. 200).';
    if (body.trim().length < 10) return 'Describe la falla con al menos 10 caracteres.';
    return null;
  };

  const takePhoto = async () => {
    const perm = await ImagePicker.requestCameraPermissionsAsync();
    if (!perm.granted) {
      setError('Se necesita permiso de cámara para capturar la evidencia en sitio.');
      return;
    }

    const result = await ImagePicker.launchCameraAsync({ base64: true, quality: 0.5 });
    if (!result.canceled && result.assets?.[0]) {
      const asset = result.assets[0];
      setPhoto({ uri: asset.uri, base64: `data:image/jpeg;base64,${asset.base64}` });
      captureLocation();
    }
  };

  const captureLocation = async () => {
    setLocationError('');
    try {
      const perm = await Location.requestForegroundPermissionsAsync();
      if (!perm.granted) {
        setLocationError('Ubicación no disponible (permiso denegado).');
        return;
      }
      const pos = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Balanced });
      setLocation(pos.coords);
    } catch (e) {
      setLocationError('No se pudo obtener la ubicación.');
    }
  };

  const handleSubmit = async () => {
    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }
    setError('');
    setLoading(true);
    try {
      await createTicket(token, {
        title: title.trim(),
        body: body.trim(),
        priority,
        photo_base64: photo?.base64,
      });
      navigation.goBack();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ padding: 20 }}>
      <FieldModeBadge />

      <Text style={styles.label}>Título</Text>
      <TextInput
        style={styles.input}
        value={title}
        onChangeText={setTitle}
        placeholder="Ej. Fuga de agua en pasillo B"
        placeholderTextColor={colors.textMuted}
      />

      <Text style={styles.label}>Descripción de la falla</Text>
      <TextInput
        style={[styles.input, styles.textarea]}
        value={body}
        onChangeText={setBody}
        placeholder="Describe lo que observaste..."
        placeholderTextColor={colors.textMuted}
        multiline
      />

      <Text style={styles.label}>Prioridad</Text>
      <View style={styles.row}>
        {PRIORITIES.map((p) => {
          const active = priority === p;
          const st = PRIORITY_STYLE[p];
          return (
            <TouchableOpacity
              key={p}
              style={[styles.chip, active && { backgroundColor: st.fg, borderColor: st.fg }]}
              onPress={() => setPriority(p)}
            >
              <Text style={[styles.chipText, active && styles.chipTextActive]}>{st.label}</Text>
            </TouchableOpacity>
          );
        })}
      </View>

      <Text style={styles.label}>Evidencia fotográfica (cámara en vivo)</Text>
      {photo?.uri ? (
        <Image source={{ uri: photo.uri }} style={styles.preview} />
      ) : (
        <View style={[styles.preview, styles.previewPlaceholder]}>
          <Text style={{ color: colors.textMuted }}>Sin evidencia capturada</Text>
        </View>
      )}

      {location && (
        <View style={styles.gpsBadge}>
          <Text style={styles.gpsText}>
            📍 Ubicación capturada: {location.latitude.toFixed(5)}, {location.longitude.toFixed(5)}
          </Text>
        </View>
      )}
      {!!locationError && <Text style={styles.gpsError}>{locationError}</Text>}

      <TouchableOpacity style={styles.cameraButton} onPress={takePhoto}>
        <Text style={styles.cameraButtonText}>📷 {photo ? 'Volver a tomar foto' : 'Tomar foto de la falla'}</Text>
      </TouchableOpacity>
      <Text style={styles.hint}>
        Solo se acepta cámara en vivo, para garantizar que la evidencia se capturó en el sitio.
      </Text>

      {!!error && <Text style={styles.error}>{error}</Text>}

      <TouchableOpacity style={styles.button} onPress={handleSubmit} disabled={loading}>
        {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>Enviar reporte</Text>}
      </TouchableOpacity>
      <TouchableOpacity style={styles.cancel} onPress={() => navigation.goBack()}>
        <Text style={styles.cancelText}>Cancelar</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  title: { fontSize: 22, fontWeight: '700', color: colors.text, marginBottom: 8 },
  label: { color: colors.textMuted, marginBottom: 6, marginTop: 14, fontSize: 13 },
  input: {
    backgroundColor: colors.surface, color: colors.text, borderRadius: 10, padding: 12,
    fontSize: 15, borderWidth: 1, borderColor: colors.border,
  },
  textarea: { height: 100, textAlignVertical: 'top' },
  row: { flexDirection: 'row', gap: 10, marginTop: 4 },
  chip: { paddingVertical: 8, paddingHorizontal: 16, borderRadius: 20, backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border },
  chipText: { color: colors.textMuted, fontSize: 13, fontWeight: '600' },
  chipTextActive: { color: '#fff' },
  preview: { width: '100%', height: 180, borderRadius: 10, marginBottom: 6, backgroundColor: colors.surface },
  previewPlaceholder: { justifyContent: 'center', alignItems: 'center', borderWidth: 1, borderColor: colors.border, borderStyle: 'dashed' },
  gpsBadge: { backgroundColor: colors.infoBg, borderRadius: 8, padding: 8, marginTop: 4 },
  gpsText: { color: colors.info, fontSize: 12, fontWeight: '600' },
  gpsError: { color: colors.textMuted, fontSize: 12, marginTop: 4 },
  cameraButton: { backgroundColor: colors.primary, borderRadius: 10, padding: 12, marginTop: 10 },
  cameraButtonText: { color: '#fff', textAlign: 'center', fontWeight: '600', fontSize: 14 },
  hint: { color: colors.textMuted, fontSize: 11, marginTop: 6, textAlign: 'center' },
  error: { color: colors.danger, marginTop: 14 },
  button: { backgroundColor: colors.primary, borderRadius: 10, padding: 14, marginTop: 20 },
  buttonText: { color: '#fff', textAlign: 'center', fontWeight: '600', fontSize: 16 },
  cancel: { padding: 14, marginBottom: 30 },
  cancelText: { color: colors.textMuted, textAlign: 'center' },
});
