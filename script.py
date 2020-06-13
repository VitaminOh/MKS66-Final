import mdl
from display import *
from matrix import *
from draw import *

"""======== first_pass( commands ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)

  Should set num_frames and basename if the frames
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.
  ==================== """
def first_pass( commands ):
    name = 'Default'
    num_frames = 1
    vary_present = False
    frames_present = False
    basename_present = False
    for x in commands:
        if 'frames' in x['op']:
            num_frames = x['args'][0]
            frames_present = True
        elif 'basename' in x['op']:
            name = x['args']
            basename_present = True
        elif 'vary' in x['op']:
            vary_present = True
    if (vary_present and not frames_present):
        print("Compile Error")
        exit()
    if (frames_present and not basename_present):
        print("WARNING: No Basename Given, Default Name Assigned")
    return (name, int(num_frames))

"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value.
  ===================="""
def second_pass( commands, num_frames, light, symbols ):
    frames = [ {} for i in range(num_frames) ]
    for x in commands:
        if x['op'] == 'vary':
            change = (int(x['args'][3]) - int(x['args'][2]))/(int(x['args'][1]) - int(x['args'][0]))
            val = x['args'][2]
            for i in range (int(x['args'][0]), int(x['args'][1])):
                frames[i][x['knob']] = val
                val += change
        elif x["op"] == "light":
            l = symbols[x["light"]][1]
            light.append([l["location"], l["color"]])
            #print (light)
    return frames


def run(filename):
    """
    This function runs an mdl script
    """
    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print("Parsing failed.")
        return

    view = [0,
            0,
            1];
    ambient = [50,
               50,
               50]
    light = [[[0.5,
              0.75,
              1],
             [255,
              255,
              255]]]

    color = [0, 0, 0]
    symbols['.white'] = ['constants',
                         {'red': [0.2, 0.5, 0.5],
                          'green': [0.2, 0.5, 0.5],
                          'blue': [0.2, 0.5, 0.5]}]
    reflect = '.white'

    (name, num_frames) = first_pass(commands)
    frames = second_pass(commands, num_frames, light, symbols)

    vertices = {}
    #print (symbols)
    for i in range(int(num_frames)):
        print("generating frame:", i)
        #print(light)
        if num_frames > 1:
            for frame in frames[i]:
                symbols[frame][1] = frames[i][frame]

        tmp = new_matrix()
        ident( tmp )

        stack = [ [x[:] for x in tmp] ]
        screen = new_screen()
        zbuffer = new_zbuffer()
        tmp = []
        step_3d = 100
        consts = ''
        coords = []
        coords1 = []

        shading_type = "flat" # GOURAUD PHONG

        for command in commands:
            # print(command)
            c = command['op']
            args = command['args']
            knob_value = 1

            if c == 'box':
                if command['constants']:
                    reflect = command['constants']
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light[:], symbols, reflect, shading_type)
                tmp = []
                reflect = '.white'
            elif c == 'cone': #makes a right cone
                if command['constants']:
                    reflect = command['constants']
                add_cone(tmp,
                            args[0], args[1], args[2], args[3], args[4], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light[:], symbols, reflect, shading_type)
                tmp = []
                reflect = '.white'
            elif c == 'sphere':
                if command['constants']:
                    reflect = command['constants']
                add_sphere(tmp,
                           args[0], args[1], args[2], args[3], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light[:], symbols, reflect, shading_type)
                tmp = []
                reflect = '.white'
            elif c == 'torus':
                if command['constants']:
                    reflect = command['constants']
                add_torus(tmp,
                          args[0], args[1], args[2], args[3], args[4], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light[:], symbols, reflect, shading_type)
                tmp = []
                reflect = '.white'
            elif c == 'line':
                add_edge(tmp,
                         args[0], args[1], args[2], args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_lines(tmp, screen, zbuffer, color)
                tmp = []
            elif c == 'move':
                x, y, z = args[0], args[1], args[2]
                if command['knob']:
                    x = x * symbols[command['knob']][1]
                    y = y * symbols[command['knob']][1]
                    z = z * symbols[command['knob']][1]
                tmp = make_translate(x, y, z)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [i[:] for i in tmp]
                tmp = []
            elif c == 'scale':
                x, y, z = args[0], args[1], args[2]
                if command['knob']:
                    x = x * symbols[command['knob']][1]
                    y = y * symbols[command['knob']][1]
                    z = z * symbols[command['knob']][1]
                tmp = make_scale(x, y, z)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [i[:] for i in tmp]
                tmp = []
            elif c == 'rotate':
                theta = args[1] * (math.pi/180) * knob_value
                if command['knob']: theta = theta * symbols[command['knob']][1]
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == "shading":
                shading_type = command["shade_type"]
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display' and num_frames == 1:
                display(screen)
            elif c == 'save' and num_frames == 1:
                save_extension(screen, args[0])
        if (num_frames > 1): save_ppm(screen, "anim/" + name[0] + "%03d" % i)
    if (num_frames > 1): make_animation(name[0])
            # end operation loop
