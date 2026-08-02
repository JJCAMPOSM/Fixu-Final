import React, { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet, Image, ActivityIndicator, ScrollView,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { createTicket } from '../api';

const PRIORITIES = ['low', 'medium', 'high'];
const PRIORITY_LABEL = { low: 'Baja', medium: 'Media', high: 'Alta' };

export default function NewTicketScreen({ token, onCreated, onCancel }) {
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  const [priority, setPriority] = useState('medium');
  const [photo, setPhoto] = useState(null); // { base64, uri }
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const validate = () => {
    if (title.trim().length < 3) return 'El título debe tener al menos 3 caracteres.';
    if (title.length > 200) return 'El título es demasiado largo (máx. 200).';
    if (body.trim().length < 10) return 'Describe la falla con al menos 10 caracteres.';
    return null;
  };

  const pickPhoto = async (fromCamera) => {
    const perm = fromCamera
      ? await ImagePicker.requestCameraPermissionsAsync()
      : await ImagePicker.requestMediaLibraryPermissionsAsync();

    if (!perm.granted) {
      setError('Se necesita permiso de cámara/galería para adjuntar la foto.');
      return;
    }

    const result = fromCamera
      ? await ImagePicker.launchCameraAsync({ base64: true, quality: 0.5 })
      : await ImagePicker.launchImageLibraryAsync({ base64: true, quality: 0.5 });

    if (!result.canceled && result.assets?.[0]) {
      const asset = result.assets[0];
      setPhoto({ uri: asset.uri, base64: `data:image/jpeg;base64,${asset.base64}` });
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
      onCreated();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ padding: 20, paddingTop: 48 }}>
      <Text style={styles.title}>Nuevo ticket de campo</Text>

      <Text style={styles.label}>Título</Text>
      <TextInput style={styles.input} value={title} onChangeText={setTitle} placeholder="Ej. Fuga de agua en pasillo B" placeholderTextColor="#6b7280" />

      <Text style={styles.label}>Descripción de la falla</Text>
      <TextInput
        style={[styles.input, styles.textarea]}
        value={body}
        onChangeText={setBody}
        placeholder="Describe lo que observaste..."
        placeholderTextColor="#6b7280"
        multiline
      />

      <Text style={styles.label}>Prioridad</Text>
      <View style={styles.row}>
        {PRIORITIES.map((p) => (
          <TouchableOpacity
            key={p}
            style={[styles.chip, priority === p && styles.chipActive]}
            onPress={() => setPriority(p)}
          >
            <Text style={[styles.chipText, priority === p && styles.chipTextActive]}>{PRIORITY_LABEL[p]}</Text>
          </TouchableOpacity>
        ))}
      </View>

      <Text style={styles.label}>Foto de la falla</Text>
      {photo?.uri && <Image source={{ uri: photo.uri }} style={styles.preview} />}
      <View style={styles.row}>
        <TouchableOpacity style={styles.secondaryButton} onPress={() => pickPhoto(true)}>
          <Text style={styles.secondaryButtonText}>Tomar foto</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.secondaryButton} onPress={() => pickPhoto(false)}>
          <Text style={styles.secondaryButtonText}>Elegir de galería</Text>
        </TouchableOpacity>
      </View>

      {!!error && <Text style={styles.error}>{error}</Text>}

      <TouchableOpacity style={styles.button} onPress={handleSubmit} disabled={loading}>
        {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>Crear ticket</Text>}
      </TouchableOpacity>
      <TouchableOpacity style={styles.cancel} onPress={onCancel}>
        <Text style={styles.cancelText}>Cancelar</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#111827' },
  title: { fontSize: 22, fontWeight: '700', color: '#fff', marginBottom: 20 },
  label: { color: '#9ca3af', marginBottom: 6, marginTop: 12, fontSize: 13 },
  input: {
    backgroundColor: '#1f2937', color: '#fff', borderRadius: 10, padding: 12,
    fontSize: 15, borderWidth: 1, borderColor: '#374151',
  },
  textarea: { height: 100, textAlignVertical: 'top' },
  row: { flexDirection: 'row', gap: 10, marginTop: 4 },
  chip: { paddingVertical: 8, paddingHorizontal: 16, borderRadius: 20, backgroundColor: '#1f2937', borderWidth: 1, borderColor: '#374151' },
  chipActive: { backgroundColor: '#4f46e5', borderColor: '#4f46e5' },
  chipText: { color: '#9ca3af', fontSize: 13 },
  chipTextActive: { color: '#fff', fontWeight: '600' },
  preview: { width: '100%', height: 180, borderRadius: 10, marginBottom: 10, backgroundColor: '#1f2937' },
  secondaryButton: { flex: 1, backgroundColor: '#1f2937', borderRadius: 10, padding: 12, borderWidth: 1, borderColor: '#374151' },
  secondaryButtonText: { color: '#fff', textAlign: 'center', fontSize: 13 },
  error: { color: '#f87171', marginTop: 14 },
  button: { backgroundColor: '#4f46e5', borderRadius: 10, padding: 14, marginTop: 20 },
  buttonText: { color: '#fff', textAlign: 'center', fontWeight: '600', fontSize: 16 },
  cancel: { padding: 14, marginBottom: 30 },
  cancelText: { color: '#9ca3af', textAlign: 'center' },
});
