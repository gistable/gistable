def Rop(y, x, v):
  """Computes an Rop.
  
  Arguments:
    y (Variable): output of differentiated function
    x (Variable): differentiated input
    v (Variable): vector to be multiplied with Jacobian from the right
  """
  w = Variable(torch.ones_like(y.data), requires_grad=True)
  return torch.autograd.grad(torch.autograd.grad(f, x, w), w, v)