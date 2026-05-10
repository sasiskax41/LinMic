package org.linmic.app.usb

import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.linmic.app.audio.MicrophoneCapture
import java.net.ServerSocket

class AdbAudioServer(private val port: Int = 38_473) {
    suspend fun serve() = withContext(Dispatchers.IO) {
        ServerSocket(port).use { server ->
            server.reuseAddress = true
            Log.i("LinMic", "ADB audio server listening on 127.0.0.1:$port")
            while (true) {
                server.accept().use { socket ->
                    socket.tcpNoDelay = true
                    val protocol = FrameProtocol(socket.getOutputStream())
                    MicrophoneCapture().stream { frame ->
                        protocol.writeFrame(frame)
                    }
                }
            }
        }
    }
}
