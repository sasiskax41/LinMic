package org.linmic.app.ui

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import androidx.activity.ComponentActivity
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import org.linmic.app.service.MicrophoneService

class MainActivity : ComponentActivity() {
    private lateinit var status: TextView

    private val permissionLauncher =
        registerForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) {
            updateStatus("Ready")
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        buildUi()
        requestPermissions()
    }

    private fun buildUi() {
        status = TextView(this).apply {
            text = "Disconnected"
            textSize = 22f
            setTextColor(0xFFF4F5F6.toInt())
        }

        val start = Button(this).apply {
            text = "Start USB streaming"
            setOnClickListener {
                ContextCompat.startForegroundService(
                    this@MainActivity,
                    Intent(this@MainActivity, MicrophoneService::class.java),
                )
                updateStatus("Streaming on USB")
            }
        }

        val stop = Button(this).apply {
            text = "Stop"
            setOnClickListener {
                stopService(Intent(this@MainActivity, MicrophoneService::class.java))
                updateStatus("Stopped")
            }
        }

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(32, 48, 32, 32)
            setBackgroundColor(0xFF15171A.toInt())
            addView(TextView(this@MainActivity).apply {
                text = "LinMic"
                textSize = 32f
                setTextColor(0xFFF4F5F6.toInt())
            })
            addView(status)
            addView(start)
            addView(stop)
        }
        setContentView(layout)
    }

    private fun requestPermissions() {
        val permissions = mutableListOf(Manifest.permission.RECORD_AUDIO)
        if (Build.VERSION.SDK_INT >= 33) {
            permissions.add(Manifest.permission.POST_NOTIFICATIONS)
        }
        val missing = permissions.filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }
        if (missing.isNotEmpty()) {
            permissionLauncher.launch(missing.toTypedArray())
        }
    }

    private fun updateStatus(value: String) {
        status.text = value
    }
}
