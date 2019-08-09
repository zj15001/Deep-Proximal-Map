import numpy as np
import sys,os
sys.path.append(os.path.join(os.getcwd(), "../util"))
from skimage.io import imread, imsave
from math import sqrt
from skimage.measure import compare_psnr
from sr_util import gauss2D, windowed_sinc, avg_filt
from construct_forward_model import construct_nonlinear_model
from mace import mace2, mace3
import matplotlib.pyplot as plt
import scipy.io as io
from math import sqrt

################### hyperparameters
clip = False
sigw = 0.1 # noise level
nl = 13
sigma_g = 10
alpha = 0.5
gamma = 2
sig = 0.05
beta = 0.2

################### Data Proe-processing
fig_in = 'test_gray'
z = np.array(imread('../'+fig_in+'.png'), dtype=np.float32) / 255.0
filt_choice = 'nonlinear'
print("filter choice: ",filt_choice)
# y = Gz. We deliberately make awgn=0 for the purpose of experiments
y = construct_nonlinear_model(z, sigma_g, alpha, sigw, gamma=gamma, clip=clip)
  # save image
figname = 'pnp_input_'+filt_choice+'.png'
fig_fullpath = os.path.join(os.getcwd(),figname)
imsave(fig_fullpath, y)
################## Plug and play ADMM iterative reconstruction
tol = 0.001
gr = (sqrt(5.)+1.)/2.
a = 0.
b = 1.
c = b - (b-a)/gr
d = a + (b-a)/gr
diff = c-d
while abs(diff) > tol:
  print("current diff = ",diff)
  if mace2(z,y,sigma_g,alpha,beta,sigw,nl,sig,gamma,clip,w=c,rho=0.8) < mace2(z,y,sigma_g,alpha,beta,sigw,nl,sig,gamma,clip,w=d,rho=0.8):
    b = d
  else:
    a = c
  c = b - (b-a)/gr
  d = a + (b-a)/gr
  diff = c-d

w_opt = (b+a)/2.
print("optimal regularizer = ",w_opt)
mse_opt = mace2(z,y,sigma_g,alpha,beta,sigw,nl,sig,gamma,clip,w=w_opt,rho=0.8,savefig=True)
print("optimal sqrt of mse: ",mse_opt)
