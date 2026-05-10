package org.linmic.app.audio

object AudioConstants {
    const val SAMPLE_RATE = 48_000
    const val CHANNELS = 1
    const val BYTES_PER_SAMPLE = 2
    const val FRAME_MS = 10
    const val FRAME_BYTES = SAMPLE_RATE * FRAME_MS / 1000 * CHANNELS * BYTES_PER_SAMPLE
}
