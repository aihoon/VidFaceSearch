#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import argparse
import json
from enum import Enum
# import time
import numpy as np
from tqdm import tqdm
import cv2
import shutil
from sklearn.metrics.pairwise import cosine_similarity
import flask

_folder_ = os.path.dirname(os.path.abspath(__file__))
_fname_ = os.path.basename(__file__)
_corename_ = os.path.splitext(_fname_)[0]
sys.path.append(_folder_)


try:
    # noinspection PyUnresolvedReferences
    from PIL import Image, ImageFont, ImageDraw
except Exception as e:
    print(f" @ Warning: PIL import error in {_fname_} - {str(e)}")


from smartxpyutils import UtilsCommon as utils
from smartxpyutils import UtilsImage as uImg
from smartxpyutils import UtilsVideo as uVid
# from smartxpyutils import UtilsSocket as uSock


Kor_font = os.path.join(_folder_, 'GmarketSansMedium.otf')

BLACK_FACE_IMG = np.zeros((128,128,3), dtype=np.uint8)


class OpMode(Enum):
    standalone = 1
    server = 11


class VidFaceSearch:

    def __init__(self, ini=None, logger=None, logging_=True, stdout_=True):

        self.ini = ini
        self.logger = logger
        self.logging_ = logging_
        self.stdout_ = stdout_

        self.description = None
        self.version = None
        self.fps = None
        self.device = 'cpu'
        self.cos_sim_thresh = 0
        self.candidate_num = 0

        self.detect_algorithm = None
        self.recog_algorithm = None

        self.detect_inst = None
        self.recog_inst = None

        self.detect_ini_fname = None
        self.recog_ini_fname = None

        self.vid_interval_msec = 0
        self.width = 0
        self.height = 0
        self.time_arr = []

        if ini:
            self.init_ini()

        if self.logger is None:
            self.logger = utils.setup_logger_with_ini(self.ini['LOGGER'],
                                                      logging_=self.logging_,
                                                      stdout_=self.stdout_)
        self.init_algorithm()

    def init_ini(self):

        self.ini = utils.remove_comments_in_ini(self.ini)
        ini = self.ini['VID_FACE_SEARCH']

        self.description = ini['description']
        self.version = ini['version']
        self.fps = float(ini['fps'])
        self.device = ini['device']

        self.cos_sim_thresh = float(ini['cos_sim_thresh'])
        self.candidate_num = float(ini['candidate_num'])

        self.detect_algorithm = ini['detect_algorithm']
        self.recog_algorithm = ini['recog_algorithm']

        self.detect_ini_fname = os.path.join(_folder_, ini['detect_ini_fname'])
        self.recog_ini_fname = os.path.join(_folder_, ini['recog_ini_fname'])

        self.vid_interval_msec = 1. / self.fps * 1000

    def init_algorithm(self):

        self.init_detect_algorithm()
        self.init_recog_algorithm()

    def init_detect_algorithm(self):

        self.logger.info(f" # {_corename_}: detection algorithm initialization with \"{self.detect_algorithm}\".")

        if self.detect_algorithm.lower() == 'minds_retinaface':
            from minds_retinaface import minds_retinaface
            ini_meta = utils.get_ini_parameters(self.detect_ini_fname)
            ini_meta['MINDS_RETINAFACE']['device'] = self.device
            self.detect_inst = minds_retinaface.Handler(ini_meta, logger=self.logger)
            self.detect_inst.device = self.device
        else:
            self.logger.error(" @ Error: incorrect detection algorithm name, {}".
                              format(self.detect_algorithm))
            sys.exit(1)

    def init_recog_algorithm(self):

        self.logger.info(f" # {_corename_}: recognition algorithm initialization with \"{self.recog_algorithm}\".")

        if self.recog_algorithm.lower() == 'minds_arcface':
            from minds_arcface import minds_arcface
            ini_meta = utils.get_ini_parameters(self.recog_ini_fname)
            ini_meta['MINDS_ARCFACE']['device'] = self.device
            self.recog_inst = minds_arcface.Handler(ini_meta, logger=self.logger)
        else:
            self.logger.error(f" @ Error: incorrect recognition algorithm name, {self.detect_algorithm}")
            sys.exit(1)

    @staticmethod
    def get_rst_img(img, face_box, obj_box, crt_time, err, t_id):

        height, width, _ = img.shape

        img = uImg.draw_box_on_img(img, face_box, color=uImg.cvRED, thickness=2)
        img = uImg.draw_box_on_img(img, obj_box, color=uImg.cvBLUE, thickness=4)
        img = uImg.put_text_twice(img, f"time: {crt_time:.1f} s", (16, height - 16),
                                  uImg.CV2_FONT, 0.5, (uImg.WHITE, uImg.BLACK), (6, 2))
        img = uImg.put_text_twice(img, f"{t_id:d}", (obj_box[0] + 8, obj_box[1] + 20),
                                  uImg.CV2_FONT, 0.5, (uImg.WHITE, uImg.BLACK), (4, 1))
        img = uImg.put_text_twice(img, f" {err:.2f}", (obj_box[0] + 8, obj_box[3] - 8),
                                  uImg.CV2_FONT, 0.5, (uImg.WHITE, uImg.BLACK), (4, 1))

        return img

    def run(self, src_vid_fname, ref_img_fname, vid_meta_fname, rst_vid_fname=None, rst_img_folder=None, tqdm_=False):

        if rst_img_folder:
            if not utils.check_folder(rst_img_folder, create_=True):
                ret_msg = f"result image folder cannot be created, {rst_img_folder}."
                return ret_msg

        rst_vid_inst = None

        if os.path.isfile(vid_meta_fname):
            with open(vid_meta_fname, 'r') as fid:
                vid_content_meta = json.load(fid)
        else:
            ret_msg = f"Meta file not found, {vid_meta_fname}."
            return ret_msg

        if os.path.isfile(src_vid_fname):
            vid_inst = cv2.VideoCapture(src_vid_fname)
            if not vid_inst.isOpened():
                ret_msg = f"Something wrong in video file, {src_vid_fname}"
                return ret_msg
        else:
            ret_msg = f"Video file not found, {src_vid_fname}."
            return ret_msg

        if os.path.isfile(ref_img_fname):
            ref_img = cv2.imread(ref_img_fname)
        else:
            ret_msg = f"Reference picture image file not found, {ref_img_fname}."
            return ret_msg

        if rst_vid_fname:
            keys = list(vid_content_meta['annotation'].keys())
            fps = float(keys[1]) - float(keys[0])
            vid_meta = vid_content_meta['video']
            rst_vid_fname_local = "test.avi"

            # noinspection PyUnresolvedReferences
            rst_vid_inst = cv2.VideoWriter(rst_vid_fname_local, cv2.VideoWriter_fourcc(*'MPEG'),
                                           fps, (int(vid_meta['width']), int(vid_meta['height'])))

        ret = self.run_core(
            vid_inst,
            ref_img,
            vid_content_meta,
            rst_vid_inst=rst_vid_inst,
            rst_img_folder=rst_img_folder,
            img_corename=utils.split_fname(src_vid_fname)[1],
            tqdm_=tqdm_)

        if isinstance(ret, str):
            return ret

        vid_inst.release()
        if rst_vid_fname:
            try:
                rst_vid_inst.release()
                uVid.convert_avi_to_mp4("test.avi")
                shutil.copy2("test.mp4", rst_vid_fname)
            except all:
                self.logger.error(f" @ Error: something wrong in result video file")

        return ret

    def run_core(
            self,
            vid_inst,
            ref_img,
            vid_meta,
            rst_vid_inst=None,
            rst_img_folder=None,
            img_corename='',
            tqdm_=False
    ):

        # get reference face vector from reference image.
        response = self.detect_inst.run(ref_img)
        ref_bbox = [int(x) for x in [x[:4] for x in response][0]]
        ref_vec = self.recog_inst.get_face_vectors([ref_img[ref_bbox[1]:ref_bbox[3],ref_bbox[0]:ref_bbox[2]]])

        rst_vid_infos = []
        pbar = None
        width = None
        height = None
        frame = None

        if tqdm_:
            pbar = tqdm(total=len(vid_meta['annotation']))

        for crt_time_idx in vid_meta['annotation']:

            f_bboxes = vid_meta['annotation'][crt_time_idx]['face']['bboxes']
            crt_time = float(crt_time_idx)
            face_imgs = []
            rst_img_infos = []

            if rst_vid_inst or f_bboxes:

                # get image from video.
                # noinspection PyUnresolvedReferences
                vid_inst.set(cv2.CAP_PROP_POS_MSEC, crt_time)
                ret, frame = vid_inst.read()
                height, width, _ = frame.shape
                if not ret:
                    ret_msg = f" @ Error: Something wrong in video - {crt_time:.3f}"
                    return ret_msg

            if f_bboxes:

                f_bboxes = uImg.denormalize_bboxes(f_bboxes, width=width, height=height)

                # collect face image array.
                for bbox in f_bboxes:
                    face_imgs.append(frame[bbox[1]:bbox[3], bbox[0]:bbox[2]])

                # get target face vectors.
                tar_vectors = self.recog_inst.get_face_vectors(face_imgs)

                # get cosine similarity.
                for idx in range(len(tar_vectors)):

                    sel = None
                    cos_sim = cosine_similarity(np.array(ref_vec).reshape(1,-1),
                                                np.array(tar_vectors[idx]).reshape(1,-1))[0][0]
                    if cos_sim < self.cos_sim_thresh:
                        continue

                    o_bboxes = vid_meta['annotation'][crt_time_idx]['object']['bboxes']
                    o_bboxes = uImg.denormalize_bboxes(o_bboxes, width=width, height=height)
                    for i, bbox in enumerate(o_bboxes):
                        ratio = uImg.get_intersection_ratio(f_bboxes[idx], bbox)
                        if ratio == 1:
                            sel = i
                            break

                    if sel is not None:
                        track_ids = vid_meta['annotation'][crt_time_idx]['object']['track_ids']
                        rst_img_infos.append([crt_time, f_bboxes[idx], cos_sim, o_bboxes[sel], track_ids[sel][0]])

                for rst_img_info in rst_img_infos:
                    rst_vid_infos.append(rst_img_info)

            if rst_vid_inst:
                if f_bboxes:
                    for rst_img_info in rst_img_infos:
                        frame = self.get_rst_img(frame, rst_img_info[1], rst_img_info[3], rst_img_info[0],
                                                 rst_img_info[2], rst_img_info[4])
                    rst_vid_inst.write(frame)

            if tqdm_:
                pbar.update(1)

        ids = []
        final_rst_vid_infos = []
        for rst_vid_info in sorted(rst_vid_infos, key=lambda x: x[2], reverse=True):
            if rst_vid_info[4] not in ids:
                final_rst_vid_infos.append(rst_vid_info)
                ids.append(rst_vid_info[4])

        if rst_img_folder:
            idx = 0
            for rst_vid_info in final_rst_vid_infos:
                frame = self.get_rst_img(frame, rst_vid_info[1], rst_vid_info[3], rst_vid_info[0], rst_vid_info[2],
                                         rst_vid_info[4])
                if idx < self.candidate_num:
                    img_fname = os.path.join(rst_img_folder,
                                             f"{idx + 1:02d}.{img_corename}.{int(rst_vid_info[0]):d}.jpg")
                    cv2.imwrite(img_fname, frame)

        return final_rst_vid_infos


def run_flask_restful_api(args):

    app = flask.Flask(__name__)
    app.config["DEBUG"] = True

    not_implemented_return = {
        "status": "fail",
        "result": "not implemented"
    }

    this = VidFaceSearch(
        ini=utils.get_ini_parameters(args.ini_fname),
        logging_=args.logging_,
        stdout_=args.stdout_
    )
    if args.candidate_num > 0:
        this.candidate_num = args.candidate_num

    server_folder = os.path.abspath(os.path.join(_folder_, "./Server.vfs/"))
    if not os.path.isdir(server_folder):
        os.makedirs(server_folder, exist_ok=True)

    @app.route('/', methods=['GET'])
    def get():
        return flask.jsonify(not_implemented_return)

    @app.route('/', methods=['PUT'])
    def put():
        return flask.jsonify(not_implemented_return)

    @app.route('/', methods=['POST'])
    def post():
        return flask.jsonify(not_implemented_return)

    @app.route('/', methods=['DELETE'])
    def delete():
        return flask.jsonify(not_implemented_return)

    @app.route("/check", methods=["POST"])
    def check():
        _dict = {
            "status": "success",
            "result": "healthy",
        }
        return flask.jsonify(_dict)

    @app.route("/run", methods=["POST"])
    def run_api():

        req = json.loads(flask.request.data.decode('utf8'))
        try:
            vid_content_meta_fname = req["vid_content_meta_url"]
            src_vid_fname = req["src_vid_url"]
            ref_img_fname = req["infected_picture_url"]
            rst_vid_fname = req["rst_vid_url"] if "rst_vid_url" in req.keys() else None
            rst_img_folder = req["rst_img_folder_url"] if "rst_img_folder_url" in req.keys() else None
            this.candidate_num = int(req['N']) if 'N' in req.keys() else 100
        except Exception as _e:
            this.logger.info(f" @ Error in handling request arguments: {_e}")
            res_json = flask.jsonify({"status": "fail", f"result": "incorrect input arguments"})
            return res_json

        ret = this.run(
            src_vid_fname,
            ref_img_fname,
            vid_content_meta_fname,
            rst_vid_fname=rst_vid_fname,
            rst_img_folder=rst_img_folder,
            tqdm_=True
        )

        if isinstance(ret, str):
            this.logger.info(f" @ Error: {ret}")
            res_json = flask.jsonify({"status": "fail", "result":  f"{ret}"})
        else:
            this.logger.info(f" # {_corename_}: success")
            ret_info = []
            for rst_vid_info in ret:
                ret_info.append(
                    [str(round(rst_vid_info[2],3)),
                     int(rst_vid_info[0]),
                     [int(x) for x in rst_vid_info[3]],
                     int(rst_vid_info[4])])

            res_json = flask.jsonify({
                "status": "success",
                "result": "ok",
                "infected_candidates": ret_info
            })

        return res_json

    app.run(host=args.ip, port=args.port, use_reloader=False)


def main(args):

    this = VidFaceSearch(
        ini=utils.get_ini_parameters(args.ini_fname),
        logging_=args.logging_,
        stdout_=args.stdout_
    )

    op_mode = OpMode[args.op_mode]

    this.logger.info("\n # {} starts in \"{}\" mode.".format(_corename_, op_mode.name))

    if op_mode == OpMode.standalone:

        ret = this.run(
            args.src_vid_fname,
            args.ref_img_fname,
            args.vid_content_meta_fname,
            rst_vid_fname=args.rst_vid_fname,
            rst_img_folder=args.rst_img_folder,
            tqdm_=True)

        print(ret)

    elif op_mode == OpMode.server:

        ini = utils.remove_comments_in_ini(utils.get_ini_parameters(args.ini_fname))
        args.ip = ini['SERVER_MODE']['ip']
        args.port = int(ini['SERVER_MODE']['port'])

        run_flask_restful_api(args)

    else:
        pass


CORENAME = "S#_5_6_7_8"
VID_CONTENT_META_FNAME = "./Input/S#_5_6_7_8/" + CORENAME + ".vcm.json"
SRC_VID_FNAME = "./Input/S#_5_6_7_8/" + CORENAME + ".mp4"
RST_VID_FNAME = "./Output/" + CORENAME + ".VidFaceSearch.mp4"
RST_IMG_FOLDER = "./Output/" + CORENAME + "/"

REF_IMG_FNAME = "./Input/S#_5_6_7_8/S#_5_6_7_8.tid_1_face.png"


def parse_arguments(argv):

    parser = argparse.ArgumentParser()

    parser.add_argument("--op_mode", default="server", choices=[x.name for x in OpMode], help="operation mode")
    parser.add_argument("--ini_fname", default=_corename_ + ".ini", help="ini filename")
    parser.add_argument("--vid_content_meta_fname", default=VID_CONTENT_META_FNAME,
                        help="Input video content meta filename")
    parser.add_argument("--src_vid_fname", default=SRC_VID_FNAME, help="Source video filename")
    parser.add_argument("--ref_img_fname", default=REF_IMG_FNAME, help="Reference picture filename")
    parser.add_argument("--rst_vid_fname", help="Result video filename", default=None)  #    RST_VID_FNAME)
    parser.add_argument("--rst_img_folder", help="Result image folder", default=RST_IMG_FOLDER)
    parser.add_argument("--candidate_num", help="Number of infected candidates", default=100)

    parser.add_argument("--runtime", default=10, type=int, help="Video processing time")

    parser.add_argument("--logging_", default=False, action='store_true', help="Logging flag")
    parser.add_argument("--stdout_", default=False, action='store_true', help="Standard output flag")

    args = parser.parse_args(argv)
    args.rst_img_folder = os.path.abspath(args.rst_img_folder)

    return args


if __name__ == "__main__":

    main(parse_arguments(sys.argv[1:]))
