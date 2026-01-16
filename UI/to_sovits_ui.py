import shutil
import streamlit as st
import os
import subprocess
import utils

def main():
    if 'so_vits_protect_root_path' not in st.session_state:
        if os.path.exists("template/json/project_path.json"):
            sovits_path = utils.load_json("template/json/project_path.json").get("sovits_path")
            if sovits_path:
                st.session_state.so_vits_protect_root_path = sovits_path
            else:
                st.session_state.so_vits_protect_root_path = ""
        else:
            st.session_state.so_vits_protect_root_path = ""
    st.write("---")
    so_vits_protect_root_path = st.text_input(
        "Enter the local so-vits-svc project root path",
        value=st.session_state.so_vits_protect_root_path,
    )
    if so_vits_protect_root_path:
        st.session_state.so_vits_protect_root_path = so_vits_protect_root_path
    utils.write_json({"sovits_path":so_vits_protect_root_path},"template/json/project_path.json")
    try:
        if so_vits_protect_root_path:
            with st.expander("View guide"):
                with open(os.path.join(so_vits_protect_root_path,"README_zh_CN.md"), 'r',encoding="utf-8") as file:
                    readme_content = file.read()
                st.markdown(readme_content)

        with st.expander("0. Prerequisites"):
            st.caption(
                "Place your voice dataset in the so-vits-svc project folder using the format below. "
                "For single-speaker training, dataset_raw only needs one speaker folder; for multi-speaker, "
                "use multiple speaker subfolders."
            )
            st.caption("Dataset folder structure:")
            st.code("""
                        dataset_raw
                        ├───speaker0
                        │   ├───xxx1-xxx1.wav
                        │   ├───...
                        │   └───Lxx-0xx8.wav
                        └───speaker1
                            ├───xx2-0xxx2.wav
                            ├───...
                            └───xxx7-xxx007.wav
                        """)
            st.caption(
                "Each audio clip should be clean, single-speaker audio (speech or singing) "
                "and trimmed to ~5-15 seconds."
            )
            st.write("---")
        with st.expander("1. Resampling"):
            st.caption(
                "The resample.py script includes resampling, mono conversion, and loudness matching. "
                "Default loudness normalization targets 0db, which can reduce quality. The pyloudnorm "
                "package does not clamp peaks, which can introduce clipping. Consider using professional "
                "audio software (e.g., Adobe Audition) for loudness matching. If you've already done this, "
                "choose 'Skip loudness matching'."
            )
            st.write("---")
            is_skip_loudnorm = st.checkbox("Skip loudness matching")
            if st.button("1. Resample"):
                if is_skip_loudnorm:
                    command = f'cd /d "{st.session_state.so_vits_protect_root_path}" && start "" "{st.session_state.so_vits_protect_root_path}/1重采样-skip_loudnorm.bat"'
                else:
                    command = f'cd /d "{st.session_state.so_vits_protect_root_path}" && start "" "{st.session_state.so_vits_protect_root_path}/1重采样.bat"'
                subprocess.Popen(command, shell=True)
        with st.expander("2. Auto-split train/val + generate config"):
            st.caption("**Loudness embedding**: Enable 'Use loudness embedding' if needed.")
            st.write("---")
            is_vol_aug = st.checkbox("Use loudness embedding")
            if st.button("2. Auto-split train/val + generate config"):
                if is_vol_aug:
                    command = f'cd /d "{st.session_state.so_vits_protect_root_path}" && start "" "{st.session_state.so_vits_protect_root_path}/2划分训练验证集-vol_aug.bat"'
                else:
                    command = f'cd /d "{st.session_state.so_vits_protect_root_path}" && start "" "{st.session_state.so_vits_protect_root_path}/2划分训练验证集.bat"'
                subprocess.Popen(command, shell=True)
        with st.expander("Open config folder"):
            if st.button("Open config folder"):
                subprocess.run(['explorer', os.path.abspath(os.path.join(st.session_state.so_vits_protect_root_path, "configs"))])
        with st.expander("3. Generate hubert + f0"):
            is_use_diff = st.checkbox("Enable shallow diffusion")
            if st.button("3. Generate hubert + f0"):
                if is_use_diff:
                    command = f'cd /d "{st.session_state.so_vits_protect_root_path}" && start "" "{st.session_state.so_vits_protect_root_path}/3生成hubert与f0_use_diff.bat"'
                else:
                    command = f'cd /d "{st.session_state.so_vits_protect_root_path}" && start "" "{st.session_state.so_vits_protect_root_path}/3生成hubert与f0.bat"'
                subprocess.Popen(command, shell=True)
        with st.expander("4. Model training"):
            col1,col2 = st.columns(2)
            is_diffusion = col1.checkbox("Train diffusion model", key=0)
            is_tensorboard = col2.checkbox("Start TensorBoard", key=1)
            if is_tensorboard:
                command = f'cd /d "{st.session_state.so_vits_protect_root_path}" && start "" "{st.session_state.so_vits_protect_root_path}/启动tensorboard.bat"'
                subprocess.Popen(command, shell=True)
            if st.button("4. Start training"):
                if is_diffusion:
                    shutil.copy2(f"{st.session_state.so_vits_protect_root_path}/pretrain/diffusion/model_0.pt",
                                 f"{st.session_state.so_vits_protect_root_path}/logs/44k/diffusion")
                    command = f'cd /d "{st.session_state.so_vits_protect_root_path}" && start "" "{st.session_state.so_vits_protect_root_path}/4模型训练_diffusion.bat"'
                else:
                    shutil.copy2(f"{st.session_state.so_vits_protect_root_path}/pretrain/vec768l12/G_0.pth", f"{st.session_state.so_vits_protect_root_path}/logs/44k")
                    shutil.copy2(f"{st.session_state.so_vits_protect_root_path}/pretrain/vec768l12/D_0.pth", f"{st.session_state.so_vits_protect_root_path}/logs/44k")
                    command = f'cd /d "{st.session_state.so_vits_protect_root_path}" && start "" "{st.session_state.so_vits_protect_root_path}/4模型训练.bat"'
                subprocess.Popen(command, shell=True)
        with st.expander("5. Model inference"):
            if st.button("Launch WebUI"):
                command = f'cd /d "{st.session_state.so_vits_protect_root_path}" && start "" "{st.session_state.so_vits_protect_root_path}/启动webUI.bat"'
                subprocess.Popen(command, shell=True)
        with st.expander("Project initialization"):
            if st.button("Initialize project"):
                folder_path_lists = [f'{st.session_state.so_vits_protect_root_path}/dataset',f'{st.session_state.so_vits_protect_root_path}/filelists',f'{st.session_state.so_vits_protect_root_path}/logs/44k',f'{st.session_state.so_vits_protect_root_path}/logs/44k/diffusion']
                for folder_path in folder_path_lists:
                    if os.path.exists(folder_path) and os.path.isdir(folder_path):
                        for filename in os.listdir(folder_path):
                            file_path = os.path.join(folder_path, filename)
                            if filename == "diffusion":
                                continue
                            try:
                                if os.path.isdir(file_path):
                                    shutil.rmtree(file_path)
                                else:
                                    os.remove(file_path)
                            except Exception as e:
                                print(f'Error deleting {file_path}: {e}')
                    else:
                        print(f'The folder {folder_path} does not exist or is not a directory.')
                st.success("Project initialized successfully.")
    except Exception as e:
        st.error(e)


if __name__ == '__main__':
    main()
