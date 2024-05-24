import glob
import os

import cv2

import numpy as np


class CameraCalibrator:

    def __init__(
            self,
            num_x_corners,
            num_y_corners,
            square_size,
            save_path='./result',
            calib_pix_tol=2.0):
        self.num_corners = (num_x_corners, num_y_corners)
        self.square_size = square_size
        self.cam_params = []
        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        self.save_path = save_path
        self.calib_pix_tol = calib_pix_tol
        self.calib_tvec_avg = [-6.09663477251606, -16.2137585916826, -17.8300732643373]
        self.calib_tvec_sd = [0.129810389218979, 0.120907581199769, 0.550938398062086]

    def initialize_save_folder(self):
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        else:
            files = glob.glob(self.save_path + '/*')
            for f in files:
                os.remove(f)

    def save_data(self, idx, img, points_2d, points_3d):
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        img_path = self.save_path + '/image_' + str(idx) + '.jpg'
        pt_2d_path = self.save_path + '/corner2d_' + str(idx) + '.txt'
        pt_3d_path = self.save_path + '/corner3d_' + str(idx) + '.txt'

        points_2d = np.array(points_2d)
        points_3d = np.array(points_3d)

        points_2d = points_2d.reshape(-1, 2)
        points_3d = points_3d.reshape(-1, 3)

        cv2.imwrite(img_path, img)
        np.savetxt(pt_2d_path, points_2d, fmt='%.4f')
        np.savetxt(pt_3d_path, points_3d, fmt='%.4f')

    def save_result(self, reproj_err, cam_mat, dcm, tvec):
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        extrinsic = np.eye(4)
        extrinsic[:3, :3] = dcm
        extrinsic[:3, 3] = tvec

        np.savetxt(self.save_path + '/reprojection_error.txt', reproj_err, fmt='%.4f')
        np.savetxt(self.save_path + '/intrinsic.txt', cam_mat, fmt='%.4f')
        np.savetxt(self.save_path + '/extrinsic.txt', extrinsic, fmt='%.4f')

    def load_data(self, img_num, path):
        imgs = []
        pts_2d = []
        pts_3d = []

        if os.path.exists(path):
            for idx in range(img_num):
                img_path = path + '/image_' + str(idx) + '.jpg'
                pt_2d_path = path + '/corner2d_' + str(idx) + '.txt'
                pt_3d_path = path + '/corner3d_' + str(idx) + '.txt'

                img = cv2.imread(img_path, cv2.IMREAD_COLOR)
                pt_2d = np.loadtxt(pt_2d_path)
                pt_3d = np.loadtxt(pt_3d_path)

                imgs.append(img)
                pts_2d.append(pt_2d)
                pts_3d.append(pt_3d)

        return imgs, pts_2d, pts_3d

    def create_checker_board(self):
        checker = []
        interval = self.square_size
        for i in range(self.num_corners[1]):
            for j in range(self.num_corners[0]):
                checker.append([j * interval, i * interval, 0.0])
        return np.array(checker)

    def find_corners(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, self.num_corners, None)
        return ret, gray, corners

    def optimize_corners(self, gray_img, corners):
        opt_corners = cv2.cornerSubPix(gray_img, corners, (11, 11), (-1, -1), self.criteria)
        return opt_corners

    def project(self, intrinsic, pose, xyz):
        proj_pts = []
        for pt in xyz:
            temp_pt = intrinsic @ np.eye(3, 4) @ pose @ np.append(pt, 1).transpose()
            proj_pt = temp_pt[:2] / temp_pt[2]
            proj_pts.append(proj_pt)
        return np.array(proj_pts)

    def convert_to_rodrigues(self, rot):
        theta = np.arccos((rot[0, 0] + rot[1, 1] + rot[2, 2] - 1) / 2)
        if abs(theta) < 1e-12:
            k = np.array([0, 0, 1])
        else:
            k = np.array([rot[2, 1] - rot[1, 2], rot[0, 2] - rot[2, 0], rot[1, 0] - rot[0, 1]])
            k = k / (2 * np.sin(theta))
        return theta * k

    def convert_to_dcm(self, rvec):
        theta = np.linalg.norm(rvec)
        k = rvec / theta
        kx = k[0]
        ky = k[1]
        kz = k[2]
        c = np.cos(theta)
        s = np.sin(theta)
        k_skew = np.array([[0, -kz, ky], [kz, 0, -kx], [-ky, kx, 0]])
        dcm = np.eye(3) + s * k_skew + (1 - c) * k_skew @ k_skew
        return dcm

    def calculate_reproj_loss(self, uv, ruv):
        a = np.linalg.norm(uv - ruv, axis=1)
        b = np.mean(a)
        c = np.sqrt(b)
        return c

    def convert_rad_to_deg(self, radian):
        degree = radian / 3.14159265 * 180
        return degree

    def convert_deg_to_rad(self, degree):
        radian = degree / 180 * 3.14159265
        return radian

    def rotate_z(self, deg):
        rad = self.convert_deg_to_rad(deg)
        c = np.cos(rad)
        s = np.sin(rad)
        rotate = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
        return rotate

    def decompose_camera_matrix(self, proj_mat):
        _, _, v = np.linalg.svd(proj_mat)
        c = v[-1] / v[-1, -1]
        kr_inv = np.linalg.inv(proj_mat[:, :3])
        q, r = np.linalg.qr(kr_inv)
        rot = q.transpose()
        intrinsic = np.linalg.inv(r)
        rot_z = self.rotate_z(180)
        intrinsic = intrinsic @ rot_z
        intrinsic /= intrinsic[2, 2]
        rot = rot_z @ rot
        c = -rot @ c[:3]
        return intrinsic, rot, c

    def direct_linear_transformation(self, uv, xyz):
        assert len(uv) == len(xyz)
        assert len(uv) >= 6
        system_mat = []
        for i in range(len(uv)):
            x, y, z = xyz[i]
            u, v = uv[i]
            system_mat.append([-x, -y, -z, -1, 0, 0, 0, 0, u*x, u*y, u*z, u])
            system_mat.append([0, 0, 0, 0, -x, -y, -z, -1, v*x, v*y, v*z, v])
        system_mat = np.array(system_mat)
        _, _, v = np.linalg.svd(system_mat)
        proj_mat = v[-1].reshape(3, 4)
        return proj_mat

    def reproject_to_image_plane_with_projection_matrix(self, proj_mat, uv, xyz):
        temp_pt = proj_mat @ np.concatenate((xyz, np.ones((xyz.shape[0], 1))), axis=1).transpose()
        reproj_pts = temp_pt[:2] / temp_pt[2]
        return reproj_pts.transpose()

    def reproject_to_image_plane(self, intrinsic, rmat, tvec, uv, xyz):
        ext = np.eye(4)
        ext[:3, :3] = rmat
        ext[:3, 3] = tvec
        proj_mat = intrinsic @ np.eye(3, 4) @ ext
        temp_pt = proj_mat @ np.concatenate((xyz, np.ones((xyz.shape[0], 1))), axis=1).transpose()
        reproj_pts = temp_pt[:2] / temp_pt[2]
        return reproj_pts.transpose()

    def calculate_intrinsics(self, points_2d, points_3d):
        proj_mat = self.direct_linear_transformation(points_2d, points_3d)
        mtx, rot, tvec = self.decompose_camera_matrix(proj_mat)
        reproj_pts = self.reproject_to_image_plane(mtx, rot, tvec, points_2d, points_3d)
        reproj_err = self.calculate_reproj_loss(points_2d, reproj_pts)
        return [reproj_err], mtx, rot, tvec

    def calculate_extrinsics(self, dcm, tvec):
        cam_to_board = np.eye(4, 4)
        cam_to_board[:3, :3] = dcm
        cam_to_board[:3, 3] = tvec
        board_to_pin = np.eye(4, 4)
        board_to_pin[0, 3] = 153.5
        board_to_pin[1, 3] = 82.5
        board_to_pin[2, 3] = -300.0
        cam_to_pin = cam_to_board @ board_to_pin
        calc_dcm = cam_to_pin[:3, :3]
        calc_tvec = cam_to_pin[:3, 3]

        return calc_dcm, calc_tvec
