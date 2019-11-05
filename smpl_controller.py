import numpy as np
import pickle
from smpl_np import SMPLModel

class Make_SMPL:
	def __init__(self,model_path):
		self.model = SMPLModel(model_path)



	def create_smpl(self,beta,pose,trans,model_n):
		self.model.set_params(beta=beta, pose=pose, trans=trans)
		self.model.save_to_obj('./smpl_np{}.obj'.format(model_n))
