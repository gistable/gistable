from android.util import TypedValue
from android.view import ViewGroup
from android.view import Gravity
from android.widget import LinearLayout
from android.widget import TextView
from android.widget import EditText
from android.widget import Button
from android.widget import ScrollView
from android.util import Log


class OnClickListener(implements=android.view.View[OnClickListener]):
    def __init__(self, text_view):
        self.text_view = text_view

    def onClick(self, v: android.view.View) -> void:
        Log.i("TESTAPP", "Push the button")
        self.text_view.setText(self.text_view.getText().toString() + "\nStop touching me!\n")
        Log.i("TESTAPP", "Text updated")


class MainActivity(extends=android.app.Activity):
    # /** Called when the activity is first created. */

    def onCreate(self, savedInstanceState: android.os.Bundle) -> void:
        super().onCreate(savedInstanceState)

        r = self.getResources()

        # #********************************************************

        layout = LinearLayout(self)

        layout.setLayoutParams(
            LinearLayout.LayoutParams(
                 LinearLayout.LayoutParams.MATCH_PARENT,
                 LinearLayout.LayoutParams.MATCH_PARENT
            )
        )

        layout.setPadding(
            TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, 16, r.getDisplayMetrics()),
            TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, 16, r.getDisplayMetrics()),
            TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, 16, r.getDisplayMetrics()),
            TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, 16, r.getDisplayMetrics())
        )
        layout.setOrientation(LinearLayout.VERTICAL)

        to_field = EditText(self)
        to_field.setLayoutParams(
            LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            )
        )
        to_field.setHint("To")

        subject_field = EditText(self)
        subject_field.setLayoutParams(
            LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            )
        )
        subject_field.setHint("Subject")

        message_field = EditText(self)
        message_field.setLayoutParams(
            LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 0, 1.0)
        )
        message_field.setGravity(Gravity.TOP)
        message_field.setHint("Message")

        send_button = Button(self)
        lp = LinearLayout.LayoutParams(
            TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, 100, r.getDisplayMetrics()),
            LinearLayout.LayoutParams.WRAP_CONTENT
        )
        lp.gravity = Gravity.RIGHT
        send_button.setLayoutParams(lp)

        send_button.setHint("Send")

        send_button.setOnClickListener(OnClickListener(message_field))

        layout.addView(to_field)
        layout.addView(subject_field)
        layout.addView(message_field)
        layout.addView(send_button)

        self.setContentView(layout)
