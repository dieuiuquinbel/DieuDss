# -*- coding: utf-8 -*-
"""
NutriDSS - VNFood 103 MobileNetV3 Training & ONNX Export Script
Target Environment: Google Colab (Free GPU T4) or Kaggle Notebook
Dataset: meowluvmatcha/vnfood-30-100 (6.95 GB on Kaggle)
Outputs:
- models/vnfood_mobilenet_v3.onnx (~12MB)
- data/vnfood_103_labels.json
"""

import os
import sys
import json
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms

def main():
    print("===================================================================")
    print("NutriDSS - VNFood 103 Fine-Grained Food Classifier (MobileNetV3)")
    print("===================================================================")

    # 1. Hardware Detection
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[*] Training Device: {device}")

    # 2. Data Directories (Default paths on Kaggle)
    # Adjust this path if running locally or on Google Colab
    dataset_dir = os.environ.get("VNFOOD_DATASET_DIR", "/kaggle/input/vnfood-30-100/vnfood_combined_dataset")
    train_dir = os.path.join(dataset_dir, "train")
    val_dir = os.path.join(dataset_dir, "val") if os.path.exists(os.path.join(dataset_dir, "val")) else os.path.join(dataset_dir, "test")

    if not os.path.exists(train_dir):
        print(f"[!] Warning: Directory '{train_dir}' not found.")
        print("[!] If running on Kaggle, add dataset 'meowluvmatcha/vnfood-30-100'.")
        print("[!] Script will create dummy architecture & export ONNX template for testing.")
        num_classes = 103
        class_names = [f"class_{i}" for i in range(103)]
    else:
        # 3. Data Transformations
        train_transforms = transforms.Compose([
            transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
            transforms.RandomHorizontalFlip(),
            transforms.ColorJitter(brightness=0.1, contrast=0.1),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

        train_dataset = datasets.ImageFolder(train_dir, transform=train_transforms)
        train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, num_workers=2, pin_memory=True)
        num_classes = len(train_dataset.classes)
        class_names = train_dataset.classes
        print(f"[*] Found {len(train_dataset)} images across {num_classes} classes.")

    # 4. Initialize Pretrained MobileNetV3-Small
    print("[*] Loading Pretrained MobileNetV3-Small...")
    weights = models.MobileNet_V3_Small_Weights.DEFAULT
    model = models.mobilenet_v3_small(weights=weights)

    # Replace classifier head for 103 classes
    in_features = model.classifier[3].in_features
    model.classifier[3] = nn.Linear(in_features, num_classes)
    model = model.to(device)

    # 5. Training Loop (Fine-tuning top layers)
    epochs = int(os.environ.get("EPOCHS", "5"))
    if os.path.exists(train_dir):
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

        print(f"[*] Starting training for {epochs} epochs...")
        for epoch in range(1, epochs + 1):
            model.train()
            running_loss = 0.0
            correct = 0
            total = 0

            for batch_idx, (inputs, targets) in enumerate(train_loader):
                inputs, targets = inputs.to(device), targets.to(device)
                optimizer.zero_grad()
                outputs = model(inputs)
                loss = criterion(outputs, targets)
                loss.backward()
                optimizer.step()

                running_loss += loss.item() * inputs.size(0)
                _, predicted = outputs.max(1)
                total += targets.size(0)
                correct += predicted.eq(targets).sum().item()

                if (batch_idx + 1) % 20 == 0:
                    print(f"Epoch [{epoch}/{epochs}] Batch [{batch_idx+1}/{len(train_loader)}] Loss: {loss.item():.4f}")

            scheduler.step()
            epoch_loss = running_loss / total
            epoch_acc = (correct / total) * 100.0
            print(f"==> Epoch {epoch}/{epochs} Complete - Loss: {epoch_loss:.4f}, Accuracy: {epoch_acc:.2f}%\n")

    # 6. Export to ONNX (~12MB)
    output_onnx_path = "vnfood_mobilenet_v3.onnx"
    print(f"[*] Exporting model to ONNX: {output_onnx_path}...")
    model.eval()
    model = model.to("cpu")
    dummy_input = torch.randn(1, 3, 224, 224, requires_grad=False)

    torch.onnx.export(
        model,
        dummy_input,
        output_onnx_path,
        export_params=True,
        opset_version=12,
        do_constant_folding=True,
        input_names=['image_input'],
        output_names=['class_probabilities'],
        dynamic_axes={'image_input': {0: 'batch_size'}, 'class_probabilities': {0: 'batch_size'}}
    )

    size_mb = os.path.getsize(output_onnx_path) / (1024 * 1024)
    print(f"[SUCCESS] Exported ONNX model successfully! Size: {size_mb:.2f} MB")
    print(f"[*] Download '{output_onnx_path}' and copy to 'NutriDSS/models/vnfood_mobilenet_v3.onnx'!")

if __name__ == "__main__":
    main()
