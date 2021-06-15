import numpy as np
import cv2

class Image ():
    def __init__(self, image_path):

        # read input as grayscale mode (0)
        self.image = cv2.imread(image_path, 0)

        # do ft 
        self.fft = np.fft.fft2(self.image)

        # apply shift of origin from upper left corner to center of image
        self.fft_shift = np.fft.fftshift(self.fft)

        # extract magnitude and phase images
        self.mag = np.abs(self.fft)
        self.phase = np.angle(self.fft)

        self.FT_Magnitude = 20*np.log(np.abs(self.fft_shift))
        self.FT_Phase = np.angle(self.fft_shift)

        # extract real and imaginary images parts
        self.real = np.real(self.fft)
        self.imaginary = np.imag(self.fft)
        
        self.FT_Real = np.real(self.fft_shift)
        self.FT_Imaginary = np.imag(self.fft_shift)

    def mix(self, Image2: 'Image', Ratio1: float, Ratio2: float, Mode: str):

        if Mode == "Magnitude_Phase":
            New_Magnitude = (self.mag * Ratio1) + (Image2.mag * (1-Ratio1))
            New_Phase = (self.phase * (1-Ratio2)) + (Image2.phase * (Ratio2))
            self.Fourier_Image_Combined = np.multiply(New_Magnitude, np.exp(1j * New_Phase))

        elif Mode == "Real_Imaginary":
            New_Real = (self.real*Ratio1) + (Image2.real*(1-Ratio1))
            New_Imaginary = (self.imaginary * (1-Ratio2)) + (Image2.imaginary * (Ratio2))
            self.Fourier_Image_Combined = New_Real + 1j * New_Imaginary

        elif Mode == "Magnitude_UniformPhase":
            self.uniphase = np.multiply(Image2.phase , 0)
            New_Magnitude = (self.mag * Ratio1) + (Image2.mag*(1-Ratio1))
            Uni_Phase = (self.uniphase*Ratio2)+(Image2.phase*(1-Ratio2))
            self.Fourier_Image_Combined = np.multiply(New_Magnitude, np.exp(1j*Uni_Phase))

        elif Mode == "UniformMagnitude_Phase":
            self.unimag = Image2.mag/Image2.mag
            Uni_Magnitude = (self.unimag*Ratio1) + (Image2.mag*(1-Ratio1))
            New_Phase = (self.phase*Ratio2) + (Image2.phase*(1-Ratio2))
            self.Fourier_Image_Combined = np.multiply(Uni_Magnitude, np.exp(1j*New_Phase))

        elif Mode == "UniformMagnitude_UniformPhase":
            self.uni_mag = Image2.mag/Image2.mag
            self.uni_phase = np.multiply(Image2.phase , 0)
            Uni_Magnitude = (self.uni_mag*Ratio1) + (Image2.mag*(1-Ratio1))
            Uni_Phase = (self.uni_phase*Ratio2) + (Image2.phase*(1-Ratio2))
            self.Fourier_Image_Combined = np.multiply(Uni_Magnitude, np.exp(1j*Uni_Phase))

        # self.f_ishift = np.fft.ifftshift(self.FourierImg)
        self.Image_Combined =np.real(np.fft.ifft2(self.Fourier_Image_Combined))
        return self.Image_Combined   
