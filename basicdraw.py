from ctypes import c_int, pointer
import os
import sdl2
import sdl2.ext as sdl2ext
import sdl2.sdlimage as sdl2image
import timeit as ti
import time

drawList = list()

# -------------------------------------------------------------------------------
# NOTE:
# w and h are only used if useimagesize == False, otherwise the loaded or duped
# texture dimensions are used.
# use parameter for EITHER imagenmae OR dupetexture -- the latter reuses (shares)
# the previously loaded texture rather than reloading it, thereby saving memory
# TODO: this "sharing" almost certainly has lifetime issues and needs to be managed
# more cleanly -- could cause a crash if a shared texture is deleted out from under
# another imageSprite using it
class imageSprite():
    def __init__(self, renderer, x, y, w, h, imagename, dupetexture, useimagesize = False):
        if imagename == '' and dupetexture is None:
            raise sdl2ext.SDLError()

        self.renderer = renderer

        if dupetexture is not None:
            self.texture = dupetexture
        else:
            fullpath = os.path.join(os.path.dirname(__file__), 'resources', imagename)
            self.texture = self._createTexture(fullpath)
        if self.texture is None:
            raise sdl2ext.SDLError()

        if useimagesize:
            # reset size if using image dimensions
            pw = pointer(c_int(0))
            ph = pointer(c_int(0))
            sdl2.SDL_QueryTexture(self.texture, None, None, pw, ph)
            w = pw.contents.value
            h = ph.contents.value
        self.dst = sdl2.SDL_Rect(x, y, w, h)
        global drawList
        drawList.append(self)

    def _createTexture(self, fullpath):
        surface = sdl2image.IMG_Load(fullpath)
        if surface is None:
            raise sdl2image.IMG_GetError()
        texture = sdl2.render.SDL_CreateTextureFromSurface(self.renderer, surface)
        if texture is None:
            raise sdl2ext.SDLError()
        sdl2.surface.SDL_FreeSurface(surface)
        return texture

    def render(self):
        sdl2.SDL_RenderCopy(self.renderer, self.texture, None, self.dst)

# -------------------------------------------------------------------------------
def render(renderer):
    # clear to black
    renderer.color = sdl2ext.Color(0, 0, 0, 255)
    renderer.clear()

    # iterate the global draw list
    for di in drawList:
        di.render()

    # test.renderTexture(image, renderer, 0, 0)
    # present renderer results
    renderer.present()

# -------------------------------------------------------------------------------
def main():
    print "Start..."

    # create window
    width = 640
    height = 480
    window = sdl2ext.Window("basicdraw", size = (width, height))
    window.show()

    renderer = sdl2ext.Renderer(window)
    # load background image first -- all others will draw over top
    backgroundSprite = imageSprite(renderer.renderer, 0, 0, 0, 0, 'background.jpg', None, True)
    furballSprite = imageSprite(renderer.renderer, 20, 20, 120, 160, 'furball.jpg', None, False)
    noseSprite = imageSprite(renderer.renderer, 320, 240, 160, 120, 'nose.bmp', None, False)
    # next two use duplicate textures
    furballDupeSprite = imageSprite(renderer.renderer, width - 150, 20, 100, 50, '', furballSprite.texture, False)
    noseDupeSprite = imageSprite(renderer.renderer, 20, height - 150, 50, 100, '', noseSprite.texture, False)

    minFrameSecs = 1.0 / 60.0
    lastDelta = 0.0
    quitLimit = 5.0
    quitTimer = 0.0

    while True:
        start = ti.default_timer()
        quitTimer += lastDelta
        if (quitTimer >= quitLimit):
            break

        render(renderer)

        stop = ti.default_timer()
        lastDelta = stop - start
        if lastDelta < minFrameSecs:
            time.sleep(minFrameSecs - lastDelta)
            stop = ti.default_timer()
            lastDelta = stop - start

    # cleanup
    print "End..."
    sdl2ext.quit()
# -------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
# -------------------------------------------------------------------------------
