import os
import sys
import zipfile
import shutil

def main():
    print("==================================================")
    print(" TikTok You (iOS) IPA Injector & Packaging Tool   ")
    print("==================================================")
    print()
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python inject_tweak.py [path_to_clean_TikTok.ipa] [path_to_tweak.dylib]")
        print()
        print("Tip: Use the GitHub Actions workflow in .github/workflows/build.yml")
        print("to automatically compile and generate ready-to-sideload IPAs!")
        return

    ipa_path = sys.argv[1]
    dylib_path = sys.argv[2]
    out_ipa = "TikTok_You_iOS_4.2.ipa"

    if not os.path.exists(ipa_path):
        print(f"Error: IPA not found: {ipa_path}")
        return
    if not os.path.exists(dylib_path):
        print(f"Error: Dylib not found: {dylib_path}")
        return

    print(f"[*] Extracting {ipa_path}...")
    temp_dir = "temp_ipa_extract"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    with zipfile.ZipFile(ipa_path, "r") as zip_ref:
        zip_ref.extractall(temp_dir)

    payload_dir = os.path.join(temp_dir, "Payload")
    app_dir = None
    for item in os.listdir(payload_dir):
        if item.endswith(".app"):
            app_dir = os.path.join(payload_dir, item)
            break

    if not app_dir:
        print("Error: Payload/*.app not found inside IPA!")
        shutil.rmtree(temp_dir)
        return

    print(f"[*] Found application bundle: {app_dir}")
    frameworks_dir = os.path.join(app_dir, "Frameworks")
    os.makedirs(frameworks_dir, exist_ok=True)

    dest_dylib = os.path.join(frameworks_dir, "BHTikTok.dylib")
    shutil.copyfile(dylib_path, dest_dylib)
    print(f"[*] Injected dylib into: {dest_dylib}")

    print(f"[*] Repacking into {out_ipa}...")
    with zipfile.ZipFile(out_ipa, "w", zipfile.ZIP_DEFLATED) as zip_out:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, temp_dir)
                zip_out.write(full_path, rel_path)

    shutil.rmtree(temp_dir)
    print(f"[+] Success! Generated: {out_ipa}")
    print("[+] Ready to sign and install with Sideloadly, AltStore, or TrollStore!")

if __name__ == "__main__":
    main()
