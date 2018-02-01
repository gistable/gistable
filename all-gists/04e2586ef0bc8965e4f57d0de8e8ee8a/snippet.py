# A simple Layer Norm implementation
# Andy Brock, March 2017
# 
# Andy's Notes:
# -This is sort of hacky but it seems to work.
# -You may also want an affine transform in there.
# -Note the .cuda() call on the dummys!
class LayerNorm(nn.Module):
    def __init__(self):
        super(LayerNorm, self).__init__()

    def forward(self, input,dummy=None):
        if dummy is None:
            dummy = torch.zeros(input.size(0)).cuda()
            dummy_var = torch.ones(input.size(0)).cuda() # These may need to be Variables

        x = input.transpose(0,1).contiguous()
        x = F.batch_norm(x,running_mean=dummy,running_var=dummy,weight=None,bias=None,training=True, momentum=0.1,eps=1e-5)
        return x.transpose(0,1)