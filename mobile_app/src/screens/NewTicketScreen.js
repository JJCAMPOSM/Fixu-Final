import React, { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet, Image, ScrollView, Alert,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import * as Location from 'expo-location';
import { Ionicons } from '@expo/vector-icons';
import { createTicket } from '../api';
import { colors, radius } from '../theme';
import { BUILDINGS, CLASSROOMS, EQUIPMENT_TYPES } from '../constants';
import Button from '../components/Button';
import SelectField from '../components/SelectField';
import { useAuth } from '../context/AuthContext';

export default function NewTicketScreen({ navigation }) {
  const { token } = useAuth();
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  const [building, setBuilding] = useState(null);
  const [classroom, setClassroom] = useState(null);
  const [equipmentType, setEquipmentType] = useState(null);
  const [photo, setPhoto] = useState(null); // { base64, uri }
  const [location, setLocation] = useState(null); // solo informativo, no se envía al servidor
  const [locationError, setLocationError] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const validate = () => {
    if (title.trim().length < 3) return 'El título debe tener al menos 3 caracteres.';
    if (title.length > 50) return 'El título es demasiado largo (máx. 50 caracteres).';
    if (body.trim().length < 10) return 'Describe la falla con al menos 10 caracteres.';
    if (body.length > 150) return 'La descripción es demasiado larga (máx. 150 caracteres).';
    if (!building) return 'Selecciona el edificio.';
    if (!classroom) return 'Selecciona el aula.';
    if (!equipmentType) return 'Selecciona el tipo de equipo.';
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
        building,
        classroom,
        equipment_type: equipmentType,
        photo_base64: photo?.base64,
      });
      Alert.alert('Reporte enviado', 'Tu reporte se envió correctamente.', [
        { text: 'OK', onPress: () => navigation.goBack() },
      ]);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ padding: 20 }}>
      <Text style={styles.label}>Título</Text>
      <TextInput
        style={styles.input}
        value={title}
        onChangeText={setTitle}
        placeholder="Ej. Fuga de agua en pasillo B"
        placeholderTextColor={colors.textMuted}
        maxLength={50}
      />
      <Text style={styles.counter}>{title.length}/50</Text>

      <Text style={styles.label}>Descripción de la falla</Text>
      <TextInput
        style={[styles.input, styles.textarea]}
        value={body}
        onChangeText={setBody}
        placeholder="Describe lo que observaste..."
        placeholderTextColor={colors.textMuted}
        maxLength={150}
        multiline
      />
      <Text style={styles.counter}>{body.length}/150</Text>

      <SelectField
        label="Edificio"
        required
        placeholder="Selecciona el edificio"
        options={BUILDINGS}
        value={building}
        onChange={setBuilding}
      />
      <SelectField
        label="Aula"
        required
        placeholder="Selecciona el aula"
        options={CLASSROOMS}
        value={classroom}
        onChange={setClassroom}
      />
      <SelectField
        label="Tipo de equipo"
        required
        placeholder="Selecciona el tipo de equipo"
        options={EQUIPMENT_TYPES}
        value={equipmentType}
        onChange={setEquipmentType}
      />

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
        <Ionicons name="camera-outline" size={18} color={colors.white} style={{ marginRight: 8 }} />
        <Text style={styles.cameraButtonText}>{photo ? 'Volver a tomar foto' : 'Tomar foto de la falla'}</Text>
      </TouchableOpacity>
      <Text style={styles.hint}>
        Solo se acepta cámara en vivo, para garantizar que la evidencia se capturó en el sitio.
      </Text>

      {!!error && <Text style={styles.error}>{error}</Text>}

      <View style={{ marginTop: 20 }}>
        <Button label="Enviar reporte" onPress={handleSubmit} loading={loading} />
      </View>
      <TouchableOpacity style={styles.cancel} onPress={() => navigation.goBack()}>
        <Text style={styles.cancelText}>Cancelar</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.pageBg },
  label: { color: colors.textSecondary, marginBottom: 6, marginTop: 14, fontSize: 13 },
  input: {
    backgroundColor: colors.white, color: colors.textPrimary, borderRadius: radius.sm, padding: 12,
    fontSize: 15, borderWidth: 1, borderColor: colors.border,
  },
  textarea: { height: 100, textAlignVertical: 'top' },
  counter: { color: colors.textMuted, fontSize: 11, textAlign: 'right', marginTop: 4 },
  preview: { width: '100%', height: 180, borderRadius: radius.sm, marginBottom: 6, backgroundColor: colors.white },
  previewPlaceholder: { justifyContent: 'center', alignItems: 'center', borderWidth: 1, borderColor: colors.border, borderStyle: 'dashed' },
  gpsBadge: { backgroundColor: colors.infoBg, borderRadius: radius.sm, padding: 8, marginTop: 4 },
  gpsText: { color: colors.info, fontSize: 12, fontWeight: '600' },
  gpsError: { color: colors.textMuted, fontSize: 12, marginTop: 4 },
  cameraButton: {
    backgroundColor: colors.accent, borderRadius: radius.sm, padding: 12, marginTop: 10,
    flexDirection: 'row', justifyContent: 'center', alignItems: 'center',
  },
  cameraButtonText: { color: colors.white, textAlign: 'center', fontWeight: '600', fontSize: 14 },
  hint: { color: colors.textMuted, fontSize: 11, marginTop: 6, textAlign: 'center' },
  error: { color: colors.danger, marginTop: 14 },
  cancel: { padding: 14, marginBottom: 30 },
  cancelText: { color: colors.textMuted, textAlign: 'center' },
});
