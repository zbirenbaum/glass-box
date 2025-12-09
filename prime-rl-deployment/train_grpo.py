import ray
import hydra
from verl.trainer.main_ppo import main
from verl.utils import fs
from omegaconf import OmegaConf

# GRPO Config for Qwen 235B
# This mimics the "DeepSeek-R1" Zero style training
config = OmegaConf.create({
    "actor_rollout_ref": {
        "model": {
            "path": "/data/models/Qwen3-235B-Instruct",
            "enable_gradient_checkpointing": True,
            "use_remove_padding": True,
        },
        "actor": {
            "strategy": "fsdp", # Use FSDP for the 235B model training
            "pp_size": 1,       # Pipeline Parallel
            "tp_size": 8,       # Tensor Parallel (Matches 1 Node)
            "gpu_per_node": 8,
        },
        "rollout": {
            "name": "vllm",
            "temperature": 1.0, # High temp for diverse reasoning paths
            "tensor_model_parallel_size": 8,
            "gpu_per_node": 8,
            "n": 64,            # Generate 64 thoughts per prompt (GRPO standard)
        },
        "ref": {
            "fsdp_config": {"param_offload": True} # Offload Ref model to CPU RAM to save VRAM
        }
    },
    "algorithm": {
        "adv_estimator": "grpo", # <--- THE KEY ALGORITHM
        "kl_ctrl": {
            "type": "fixed",
            "kl_coef": 0.001
        }
    },
    "trainer": {
        "total_epochs": 1,
        "total_training_steps": 500,
        "project_name": "qwen-235b-grpo",
        "default_hdfs_dir": "/data/models/checkpoints",
        # RAY PLACEMENT LOGIC
        "nnodes": 12,
        "save_freq": 10,
        "test_freq": 10,
    }
})

if __name__ == "__main__":
    # We don't need to manually specifying resources here because 
    # Prime-RL's config automatically requests the Ray Actors.
    # The 4 Trainer nodes will pick up the FSDP Actors.
    # The 8 Generator nodes will pick up the vLLM Rollout Actors.
    ray.init(address="auto")
    main(config)
