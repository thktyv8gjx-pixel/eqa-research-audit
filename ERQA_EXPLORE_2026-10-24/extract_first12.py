"""Offline ERQA extraction: first 12 records, CRC checks, original image bytes.

Run with private/.venv/bin/python extract_first12.py from this directory.
Requires tfrecord, crc32c, Pillow; TensorFlow and network access are unused.
"""
import hashlib
import io
import json
import struct
from pathlib import Path

import crc32c
from PIL import Image, ImageDraw, ImageOps
from tfrecord import example_pb2

ROOT = Path(__file__).resolve().parent
PRIVATE = ROOT / "private"
SOURCE = "https://raw.githubusercontent.com/embodiedreasoning/ERQA/main/data/erqa.tfrecord"
REVISION = "5bba488252c5b345a43335bfb9239b6bf12bd91c"
FULL_SIZE = 91402921
FULL_BLOB = "4ffb6604019b5f20b3428f8dd4cd2cb07e8cb6a8"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def masked_crc(data):
    value = crc32c.crc32c(data)
    return (((value >> 15) | (value << 17)) + 0xA282EAD8) & 0xFFFFFFFF


def main():
    received = (PRIVATE / "erqa.tfrecord.part").read_bytes()
    if len(received) == FULL_SIZE:
        blob = hashlib.sha1(f"blob {FULL_SIZE}\0".encode() + received).hexdigest()
        assert blob == FULL_BLOB, "Complete file does not match upstream Git blob"
    out = PRIVATE / "first12"
    out.mkdir(exist_ok=True)
    records, tiles, offset = [], [], 0
    for index in range(12):
        start = offset
        assert offset + 12 <= len(received), f"Incomplete header at row {index}"
        length_bytes = received[offset:offset + 8]
        size = struct.unpack("<Q", length_bytes)[0]
        assert offset + 16 + size <= len(received), f"Incomplete row {index}"
        assert struct.unpack_from("<I", received, offset + 8)[0] == masked_crc(length_bytes)
        payload = received[offset + 12:offset + 12 + size]
        assert struct.unpack_from("<I", received, offset + 12 + size)[0] == masked_crc(payload)
        offset += size + 16
        features = example_pb2.Example.FromString(payload).features.feature
        text = lambda key: [b.decode("utf-8") for b in features[key].bytes_list.value]
        questions, answers = text("question"), text("answer")
        assert len(questions) == len(answers) == 1
        assert questions[0].strip() and answers[0].strip() in "ABCD" and len(answers[0].strip()) == 1
        encoded = features["image/encoded"].bytes_list.value
        assert encoded, f"No images for row {index}"
        images = []
        for image_index, data in enumerate(encoded):
            with Image.open(io.BytesIO(data)) as check:
                check.verify()
            with Image.open(io.BytesIO(data)) as im:
                im.load()
                fmt, dimensions = im.format, list(im.size)
                extension = {"JPEG": "jpg", "PNG": "png", "WEBP": "webp"}.get(fmt, "bin")
                filename = f"row{index:03d}_image{image_index:02d}.{extension}"
                (out / filename).write_bytes(data)
                tile = Image.new("RGB", (320, 260), "white")
                tile.paste(ImageOps.contain(im.convert("RGB"), (320, 230)), (0, 25))
                ImageDraw.Draw(tile).text((5, 5), f"row {index} / image {image_index}", fill="black")
                tiles.append(tile)
            images.append({"path": filename, "sha256": digest(data), "size": len(data),
                           "dimensions": dimensions, "format": fmt, "decoded": True})
        visual_indices = list(features["visual_indices"].int64_list.value)
        assert not visual_indices or len(visual_indices) == len(images)
        assert all(0 <= i <= len(questions[0]) for i in visual_indices)
        record = {"row_index": index, "question": questions[0], "answer": answers[0],
                  "question_type": text("question_type"), "visual_indices": visual_indices,
                  "images": images, "byte_offset": start, "record_end": offset,
                  "payload_sha256": digest(payload), "crc32c_verified": True,
                  "feature_names": sorted(features)}
        records.append(record)
        print(json.dumps(record, ensure_ascii=False))
    (out / "examples.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records))
    prefix = received[:offset]
    (PRIVATE / "first12.tfrecord").write_bytes(prefix)
    provenance = {"source_url": SOURCE, "source_commit": REVISION,
                  "pinned_source_url": SOURCE.replace("/main/", f"/{REVISION}/"),
                  "upstream_full_size": FULL_SIZE, "upstream_full_git_blob": FULL_BLOB,
                  "received_file_size": len(received), "received_sha256": digest(received),
                  "complete_upstream_file": len(received) == FULL_SIZE,
                  "full_upstream_git_blob_verified": len(received) == FULL_SIZE,
                  "extracted_prefix_bytes": offset, "extracted_prefix_sha256": digest(prefix),
                  "records": 12, "all_record_crcs_verified": True,
                  "images": sum(len(r["images"]) for r in records),
                  "license": "CC BY 4.0; see upstream LICENSE",
                  "integrity_limit": "Record CRCs are verified; full upstream blob hash is not verified for a partial download."}
    (PRIVATE / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    sheet = Image.new("RGB", (320 * 4, 260 * ((len(tiles) + 3) // 4)), "#dddddd")
    for i, tile in enumerate(tiles):
        sheet.paste(tile, ((i % 4) * 320, (i // 4) * 260))
    sheet.save(PRIVATE / "contact_sheet.jpg")
    print(json.dumps(provenance, indent=2))


if __name__ == "__main__":
    main()
