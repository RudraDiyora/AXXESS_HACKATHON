import { Stack } from 'expo-router';

export default function VisitLayout() {
  return (
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Screen name="[id]" />
      <Stack.Screen name="summary" />
      <Stack.Screen name="diagnoses" />
      <Stack.Screen name="meds" />
      <Stack.Screen name="labs" />
      <Stack.Screen name="appointments" />
      <Stack.Screen name="transcript" />
    </Stack>
  );
}
