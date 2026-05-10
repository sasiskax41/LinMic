package org.linmic.app.usb

import java.io.OutputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder

class FrameProtocol(private val output: OutputStream) {
    private var sequence = 0L

    fun writeFrame(frame: ByteArray) {
        val header = ByteBuffer.allocate(12).order(ByteOrder.LITTLE_ENDIAN)
        header.putInt(frame.size)
        header.putLong(sequence++)
        output.write(header.array())
        output.write(frame)
        output.flush()
    }
}
