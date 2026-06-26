from pycaw.pycaw import AudioUtilities

devices = AudioUtilities.GetSpeakers()

volume = devices.EndpointVolume

print(volume.GetVolumeRange())