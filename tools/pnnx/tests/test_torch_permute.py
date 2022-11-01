# Tencent is pleased to support the open source community by making ncnn available.
#
# Copyright (C) 2021 THL A29 Limited, a Tencent company. All rights reserved.
#
# Licensed under the BSD 3-Clause License (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
# https://opensource.org/licenses/BSD-3-Clause
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import torch
import torch.nn as nn
import torch.nn.functional as F
from packaging import version

class Model(nn.Module):
    def __init__(self):
        super(Model, self).__init__()

    def forward(self, x, y, z):
        if version.parse(torch.__version__) < version.parse('1.9'):
            x = x.permute(1, 0, 2)
            x = x.permute(0, 1, 2)
            y = y.permute(2, 3, 1, 0)
            y = y.permute(3, 1, 0, 2)
            z = z.permute(1, 3, 0, 4, 2)
            z = z.permute(0, 2, 4, 3, 1)
        else:
            x = torch.permute(x, (1, 0, 2))
            x = torch.permute(x, (0, 1, 2))
            y = torch.permute(y, (2, 3, 1, 0))
            y = torch.permute(y, (3, 1, 0, 2))
            z = torch.permute(z, (1, 3, 0, 4, 2))
            z = torch.permute(z, (0, 2, 4, 3, 1))
        return x, y, z

def test():
    net = Model()
    net.eval()

    torch.manual_seed(0)
    x = torch.rand(1, 3, 16)
    y = torch.rand(1, 5, 9, 11)
    z = torch.rand(14, 8, 5, 9, 10)

    a = net(x, y, z)

    # export torchscript
    mod = torch.jit.trace(net, (x, y, z))
    mod.save("test_torch_permute.pt")

    # torchscript to pnnx
    import os
    os.system("../src/pnnx test_torch_permute.pt inputshape=[1,3,16],[1,5,9,11],[14,8,5,9,10]")

    # pnnx inference
    import test_torch_permute_pnnx
    b = test_torch_permute_pnnx.test_inference()

    for a0, b0 in zip(a, b):
        if not torch.equal(a0, b0):
            return False
    return True

if __name__ == "__main__":
    if test():
        exit(0)
    else:
        exit(1)
