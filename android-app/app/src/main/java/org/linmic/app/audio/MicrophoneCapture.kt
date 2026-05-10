package org.linmic.app.audio

import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import kotlinx.coroutines.isActive
import kotlinx.coroutines.yield
import kotlin.coroutines.coroutineContext

class MicrophoneCapture {
    suspend fun stream(onFrame: suspend (ByteArray) -> Unit) {
        val minBuffer = AudioRecord.getMinBufferSize(
            AudioConstants.SAMPLE_RATE,
            AudioFormat.CHANNEL_IN_MONO,
            AudioFormat.ENCODING_PCM_16BIT,
        )
        val bufferSize = maxOf(minBuffer, AudioConstants.FRAME_BYTES * 4)
        val recorder = AudioRecord.Builder()
            .setAudioSource(MediaRecorder.AudioSource.VOICE_RECOGNITION)
            .setAudioFormat(
                AudioFormat.Builder()
                    .setSampleRate(AudioConstants.SAMPLE_RATE)
                    .setChannelMask(AudioFormat.CHANNEL_IN_MONO)
                    .setEncoding(AudioFormat.ENCODING_PCM_16BIT)
                    .build()
            )
            .setBufferSizeInBytes(bufferSize)
            .build()

        val frame = ByteArray(AudioConstants.FRAME_BYTES)
        recorder.startRecording()
        try {
            while (coroutineContext.isActive) {
                val read = recorder.read(frame, 0, frame.size)
                if (read > 0) {
                    onFrame(frame.copyOf(read))
                } else {
                    yield()
                }
            }
        } finally {
            recorder.stop()
            recorder.release()
        }
    }
}
