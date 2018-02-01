from javax.swing import JFrame, JLabel, SwingUtilities


class HelloWorldSwing(implements=java.lang.Runnable):
    def run(self) -> void:
        self.createAndShowGUI()

    def createAndShowGUI(self):
        frame = JFrame("HelloWorldSwing")
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE)

        label = JLabel("Hello World")
        frame.getContentPane().add(label)

        frame.pack()
        frame.setVisible(True)


class MainThread(extends=java.lang.Thread):
    @super({target=target, name='main'})
    def __init__(self, target: java.lang.Runnable) -> void:
        pass
    