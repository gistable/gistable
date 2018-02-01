#https://gist.github.com/stared/dfb4dfaf6d9a8501cd1cc8b8cb806d2e
class PlotLosses(keras.callbacks.Callback):
    
    def __init__(self,imgs):
        super(PlotLosses, self).__init__()
        self.imgs=imgs
    
    def on_train_begin(self, logs={}):
        self.i = 0
        self.x = []
        self.losses = []
        self.val_losses = []
        
        self.fig = plt.figure()
        
        self.logs = []
        
    def draw(self):
        preds=model.predict(self.imgs[:1])
        plt.imshow(self.imgs[0])
        plt.imshow(np.argmax(preds.reshape([224,224,2]),axis=-1),alpha=0.6)
        
    def on_batch_end(self,batch,logs={}):
        clear_output(wait=True)
        self.draw()
        plt.show();
        
        
    def on_epoch_end(self, epoch, logs={}):
        
        self.logs.append(logs)
        self.x.append(self.i)
        self.losses.append(logs.get('loss'))
        self.val_losses.append(logs.get('val_loss'))
        self.i += 1
        
        clear_output(wait=True)
        plt.plot(self.x, self.losses, label="loss")
        plt.plot(self.x, self.val_losses, label="val_loss")
        plt.legend()
        plt.show();
        
        #gidi
        
        
plot_losses = PlotLosses(imgs[:1])