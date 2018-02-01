import numpy as np

def softmax(x):
    exp_x = np.exp(x.T-x.max(1))
    return (exp_x/exp_x.sum(0)).T

class Sgd:
    def __init__(self,eta=0.01):
        self.eta = eta
        
    def __call__(self,w,g):
        w += -self.eta*g

class Mmtsgd:
    def __init__(self,eta=0.01,mmt=0.9):
        self.eta = eta
        self.mmt = mmt
        self.dw = 0
    
    def __call__(self,w,gw):
        self.dw = self.mmt*self.dw-self.eta*gw
        w += self.dw
        
class Nag:
    def __init__(self,eta=0.01,mmt=0.9):
        self.eta = eta
        self.mmt = mmt
        self.dw = 0
        self.gw0 = np.nan
    
    def __call__(self,w,gw):
        if(self.gw0 is np.nan):
            self.gw0 = gw
        self.dw = self.mmt*self.dw-self.eta*(gw+self.mmt*(gw-self.gw0))
        self.gw0 = gw
        w += self.dw

class Adagrad:
    def __init__(self,eta=0.01):
        self.eta = eta
        self.G = 1e-7
    
    def __call__(self,w,gw):
        self.G += gw**2
        w += -self.eta*gw/np.sqrt(self.G)

class Adadelta:
    def __init__(self,eta=0.01,rho=0.95):
        self.eta = eta
        self.rho = rho
        self.G = 1e-7
    
    def __call__(self,w,gw):
        self.G = self.rho*self.G+(1-self.rho)*gw**2
        w += -self.eta*gw/np.sqrt(self.G)

class Adam:
    def __init__(self,eta=0.001,beta1=0.9,beta2=0.999):
        self.eta = eta
        self.beta1 = beta1
        self.beta2 = beta2
        self.i = 1
        self.m = 0
        self.v = 1e-7
    
    def __call__(self,w,gw):
        self.m = self.beta1*self.m+(1-self.beta1)*gw
        self.v = self.beta2*self.v+(1-self.beta2)*gw**2
        w += -self.eta*np.sqrt(1-self.beta2**self.i)/(1-self.beta1**self.i)*self.m/(np.sqrt(self.v))
        self.i += 1



class ThotthoiLogistic:
    def __init__(self,eta=0.1,opt='Sgd',n_thamsam=1000,n_batch=100,loss='entropy',reg='l2',l=10,std=False,ro=0,dukha='maen_truat',bok=1):
        '''
        eta: อัตราการเรียนรู้
        opt: ออปทิไมเซอร์
        n_thamsam: จำนวนครั้งที่จะทำซ้ำเพื่อเรียนรู้
        n_batch: ขนาดของมินิแบตช์
        loss: ชนิดของค่าเสียหาย entropy หรือ mse (ค่าเฉลี่ยผลรวมความคลาดเคลื่อนกำลังสอง)
        reg: ชนิดของเรกูลาไรซ์
        l: ขนาดของเรกูลาไรซ์
        std: จะทำให้เป็นมาตรฐานหรือไม่
        ro: รอให้ไม่มีอะไรดีขึ้นกี่ครั้งจึงจะสิ้นสุดการเรียนรู้
        dukha: จะใช้ค่าอะไรเป็นตัวกำหนดเงื่อนไขการหยุด
        bok: จะบอกผล 1 ครั้งต่อกี่ขั้นการฝึก
        '''
        
        self.n_thamsam = n_thamsam
        self.n_batch = n_batch
        if(type(opt)==str):
            if(eta<=0):
                eta = 0.1
            o = {'Sgd':Sgd,'Mmtsgd':Mmtsgd,'Nag':Nag,
                 'Adagrad':Adagrad,'Adadelta':Adadelta,'Adam':Adam}
            opt = o[opt.capitalize()](eta)
        self.opt = opt
        if(loss not in ['entropy','mse']):
            loss = 'entropy'
        self.loss = loss
        if(reg not in ['l1','l2']):
            reg = 'l2'
        self.reg = reg
        if(l<0):
            l = 0
        self.l = l
        self.std = std
        if(ro<0):
            ro =0
        self.ro = ro
        if(dukha not in ['maen_truat','maen_fuek','khasiahai']):
            dukha = 'maen_truat'
        self.dukha = dukha
        self.bok = bok

    def rianru(self,X,z,X_truat=0,z_truat=0,rianto=0,n_thamsam=0,n_batch=-1,opt=0,loss=0,reg=0,l=-1,std=-1,ro=-1,dukha=0,bok=-1):
        '''
        ฟังก์ชันสำหรับเริ่มการเรียนรู้
        X: ค่าตัวแปรต้นที่ใช้ในการฝึก
        z: ค่าผลลัพธ์ที่ใช้ในการฝึก
        X_truat: ค่าตัวแปรต้นที่ใช้ในการตรวจสอบ
        z_truat: ค่าผลลัพธ์ที่ใช้ในการตรวจสอบ
        rianto: จะให้เริ่มเรียนรู้ใหม่หรือต่อจากเดิม
        '''
        if(n_thamsam==0):
            n_thamsam = self.n_thamsam
        if(n_batch==-1):
            n_batch = self.n_batch
        if(opt<=0):
            opt = self.opt
        if(loss==0 or loss not in ['entropy','mse']):
            loss = self.loss
        if(reg==0 or reg not in ['l1','l2']):
            reg = self.reg
        if(l<0):
            l = self.l
        if(std==-1):
            std = self.std
        if(ro<0):
            ro = self.ro
        if(bok==-1):
            bok = self.bok
        if(dukha==0 or dukha not in ['maen_truat','maen_fuek','khasiahai']):
            dukha = self.dukha
        
        n = len(z)
        if(type(X_truat)!=np.ndarray): # ถ้าไม่ได้ป้อนข้อมูลตรวจสอบมาด้วย ก็ให้ใช้ข้อมูลฝึกฝนเป็นข้อมูลตรวจสอบ
            X_truat,z_truat = X,z
        if(n_batch==0 or n<n_batch):
            n_batch = n
            
        if(std):
            X_std = X.std(0)
            X_std[X_std==0] = 1
            X_mean = X.mean(0)
            X = (X-X_mean)/X_std
            X_truat = (X_truat-X_mean)/X_std
        
        if(z.ndim>1):
            z = z.argmax(1)
        self.kiklum = int(z.max()+1)
        z_1h = z[:,None]==range(self.kiklum)
        
        # ถ้าเลือกให้เรียนรู้ใหม่ก็ล้างน้ำหนักเป็นศูนย์ให้หมด
        if(rianto==0 or 'w' not in self.__dict__):
            self.w = np.zeros([X.shape[1]+1,self.kiklum])
        self.gw = self.w.copy()
        
        # หากเป็นการเรียนรู้ครั้งแรก หรือถ้าหากไม่ได้เลือกเรียนต่อจากที่เคยเรียนไว้แล้วก็ให้สร้างลิสต์บันทึกค่าเสียหายและความแม่นยำใหม่
        if(rianto==0 or 'khasiahai' not in self.__dict__):
            self.khasiahai = []
            self.maen_fuek = []
            self.maen_truat = []
        dimaksut = -np.inf # ค่าจำนวนที่ถูกมากสุด
        maiphoem = 0 # นับว่าจำนวนที่ถูกไม่เพิ่มมาแล้วกี่ครั้ง
        for j in range(n_thamsam):
            lueak = np.random.permutation(n)
            for i in range(0,n,n_batch):
                Xn = X[lueak[i:i+n_batch]]
                zn = z_1h[lueak[i:i+n_batch]]
                phi = self.ha_softmax(Xn)
                
                if(loss=='entropy'):
                    eee = (phi-zn)/len(zn)
                    self.gw[1:] = np.dot(eee.T,Xn).T
                    self.gw[0] = eee.sum(0)
                else:
                    for k in range(self.kiklum):
                        delta_nm = np.zeros(self.kiklum)
                        delta_nm[k] = 1
                        eee = 2*(phi*(phi[:,k:k+1]-delta_nm)*(zn-phi)).sum(1)
                        self.gw[1:,k] = (eee[:,None]*Xn).mean(0)
                        self.gw[0,k] = eee.mean()
                
                if(l>0):
                    if(reg=='l1'):
                        self.gw[1:] += (self.w[1:]!=0)*np.where(self.w[1:]>0,1,-1)*l/n
                    else:
                        self.gw[1:] += 2*self.w[1:]*l/n
                
                opt(self.w,self.gw)
                #self.w = self.w-self.gw*eta
            
            # หาค่าเสียหายและความแม่นยำในการทายข้อมูลฝึกและข้อมูลตรวจสอบ
            khasiahai = self.ha_khasiahai(X,z_1h,reg,l)
            maen_fuek = self.ha_khwammaen(X,z)
            maen_truat = self.ha_khwammaen(X_truat,z_truat)
            
            di = {'maen_truat':maen_truat,'maen_fuek':maen_fuek,'khasiahai':-khasiahai}[dukha]
            
            if(di > dimaksut):
                # ถ้าจำนวนที่ถูกมากขึ้นกว่าเดิมก็บันทึกค่าจำนวนนั้น และน้ำหนักในตอนนั้นไว้
                dimaksut = di
                maiphoem = 0
                w = self.w.copy()
            else:
                maiphoem += 1 # ถ้าไม่ถูกมากขึ้นก็นับไว้ว่าไม่เพิ่มไปอีกครั้งแล้ว
            
            self.khasiahai.append(khasiahai)
            self.maen_fuek.append(maen_fuek)
            self.maen_truat.append(maen_truat)
            # ถ้าหากตั้งไว้ว่าให้บอกความคืบหน้าก็ให้พิมพ์ข้อความออกมาตามความถี่ตามที่กำหนดไว้
            if(bok>0 and int(j%bok)==0):
                if(dukha=='khasiahai'):
                    print(u'ครั้งที่ %d ถูก %.3e สูงสุด %.3e ไม่ลดมาแล้ว %d ครั้ง'%(j+1,-di,-dimaksut,maiphoem))
                else:
                    print(u'ครั้งที่ %d ถูก %.3f%% สูงสุด %.3f%% ไม่เพิ่มมาแล้ว %d ครั้ง'%(j+1,di,dimaksut,maiphoem))
            
            if(ro>0 and maiphoem>=ro):
                break # ถ้าจำนวนที่ถูกไม่เพิ่มเลย 10 ครั้งก็เลิกทำ
                
        self.w = w # ค่าน้ำหนักที่ได้ในท้ายสุด เอาตามค่าที่ทำให้ทายถูกมากที่สุด
        
        if(std):
            self.w[1:] /= X_std[:,None]
            self.w[0] -= (self.w[1:]*X_mean[:,None]).sum(0)

    def thamnai(self,X):
        return (np.dot(X,self.w[1:])+self.w[0]).argmax(1)

    def ha_softmax(self,X):
        return softmax(np.dot(X,self.w[1:])+self.w[0])
    
    thamnai_laiat = ha_softmax
    
    def ha_khasiahai(self,X,z,reg,l):
        if(self.loss=='entropy'):
            khasiahai = self.ha_entropy(X,z)
        else:
            khasiahai = self.ha_mse(X,z)
        if(l!=0):
            if(reg=='l1'):
                khasiahai += l*np.abs(self.w[1:]).sum()
            else:
                khasiahai += l*((self.w[1:])**2).sum()
        return khasiahai
    
    def ha_entropy(self,X,z):
        return -(z*np.log(self.ha_softmax(X)+1e-7)).mean()
    
    def ha_mse(self,X,z):
        return ((z-self.ha_softmax(X))**2).mean()
    
    def ha_khwammaen(self,X,z):
        return (self.thamnai(X)==z).mean()*100