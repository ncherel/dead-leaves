# Simple dead leaves image generation

Dead leaves images are simple synthetic images built from stacking shapes on top of one another.
These images are useful because with statistics matching those of natural images[1](https://arxiv.org/abs/math/0312035). They are used for camera evaluation[2](https://standards.ieee.org/ieee/1858/6931/) or deep learning training[3](https://link.springer.com/chapter/10.1007/978-3-031-31975-4_24).

![](dead_leaves.png =500x)

Here, you can find two implementations based on simple primitives from a computer graphics perspective i.e. simply stacking circles:
- the first one `leaves_pillow.py` simply relies on Pillow and the ImageDraw module
- the second one `leaves_opengl.py` uses PyOpenGL and instance drawing. Thanks to John Parker for his [blogpost on drawing many circles](https://www.johnaparker.com/blog/circle-graphics).

Both methods sample disks with the same power parameter $alpha = 3.0$. Colors are randomly sampled in the RGB cube but can be easily controlled.


## Benchmark

Time for generating 100 images of size 1000x1000.

| N disks | Pillow | PyOpenGL |
| 2000    | 8.27s  | 7.74s    |
| 10000   | 18.88s | 8.56s    |

The difference in performance is not striking for low disk numbers, most time is spent writing the images to disks.
The low-level implementation based on OpenGL is only marginally faster but could be a good starting point for complex shapes, textures, colors which are not available through Pillow's API (if speed is an issue).

## Limitations

These implementations only support disks with simple color schemes (no gradients or complex blurs).
For more appearance parameters, we refer the reader to the work of R. Achddou: [Hybrid Training of Denoising Networks to Improve the Texture Acutance of Digital Cameras](https://github.com/rachddou/acutance_loss), and [VibrantLeaves : A principled parametric image generator for training deep restoration models](https://github.com/rachddou/DeadLeavesPlus).





