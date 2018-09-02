import imsciutils

class CameraReadError(ValueError):
    pass

class InvalidInterpolationType(ValueError):
    def __init__(self,interp):
        interp_string = """cv2.INTER_NEAREST --> {}
                        cv2.INTER_LINEAR --> {}
                        cv2.INTER_AREA --> {}
                        cv2.INTER_CUBIC --> {}
                        cv2.INTER_LANCZOS4 --> {}""".format(cv2.INTER_NEAREST,
                                                            cv2.INTER_LINEAR,
                                                            cv2.INTER_AREA,
                                                            cv2.INTER_CUBIC,
                                                            cv2.INTER_LANCZOS4,)
        error_string = "'interpolation' ({}) must be one of the following!"\
                                                            .format(interp)
        error_string = error_string + '\n' + interp_string
        imsciutils.error(error_string)
        super(InvalidInterpolationType,self).__init__(error_string)
