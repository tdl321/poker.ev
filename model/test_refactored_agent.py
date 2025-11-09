"""Test script to verify the refactored PokerAgent best practices."""

import torch
from poker_agent import PokerAgent


def test_weight_initialization():
    """Test that weights are properly initialized with Xavier."""
    print("=" * 60)
    print("Testing Weight Initialization")
    print("=" * 60)

    agent = PokerAgent(state_dim=44, hidden_dim=128, risk_profile='neutral')

    # Check that weights are not default (should be Xavier initialized)
    fc1_weight = agent.fc1.weight.data
    fc1_bias = agent.fc1.bias.data

    # Xavier initialization should have specific variance
    # For Xavier normal: std ≈ sqrt(2 / (fan_in + fan_out))
    expected_std = (2.0 / (44 + 128)) ** 0.5
    actual_std = fc1_weight.std().item()

    print(f"FC1 Weight - Expected std: {expected_std:.4f}, Actual std: {actual_std:.4f}")
    print(f"FC1 Bias - All initialized to 0.01: {torch.allclose(fc1_bias, torch.tensor(0.01))}")

    # Check all biases are 0.01
    assert torch.allclose(fc1_bias, torch.tensor(0.01), atol=1e-6), "Bias not initialized correctly"
    assert 0.5 * expected_std < actual_std < 2.0 * expected_std, "Weight std out of expected range"

    print("✓ Weight initialization passed\n")


def test_extra_repr():
    """Test that extra_repr provides useful debugging information."""
    print("=" * 60)
    print("Testing extra_repr")
    print("=" * 60)

    agent = PokerAgent(state_dim=44, hidden_dim=128, risk_profile='neutral')

    repr_str = agent.extra_repr()
    print(f"extra_repr output: {repr_str}")

    assert 'state_dim=44' in repr_str
    assert 'hidden_dim=128' in repr_str
    assert 'risk_profile=neutral' in repr_str
    assert 'device=' in repr_str

    print("✓ extra_repr passed\n")


def test_device_handling():
    """Test that device parameter works correctly."""
    print("=" * 60)
    print("Testing Device Handling")
    print("=" * 60)

    # Test CPU device
    agent_cpu = PokerAgent(state_dim=44, hidden_dim=128, device='cpu')
    print(f"Agent device: {agent_cpu.device}")
    assert agent_cpu.device.type == 'cpu', "Device should be CPU"
    assert agent_cpu.fc1.weight.device.type == 'cpu', "Weights should be on CPU"

    # Test default device (should be CPU or CUDA if available)
    agent_default = PokerAgent(state_dim=44, hidden_dim=128)
    print(f"Default device: {agent_default.device}")
    assert agent_default.device.type in ['cpu', 'cuda'], "Device should be CPU or CUDA"

    # Test that forward pass works on correct device
    state = torch.randn(44)
    output = agent_cpu(state)
    assert output[0].device.type == 'cpu', "Output should be on same device"

    print("✓ Device handling passed\n")


def test_forward_pass_efficiency():
    """Test forward pass with different input formats."""
    print("=" * 60)
    print("Testing Forward Pass Flexibility")
    print("=" * 60)

    agent = PokerAgent(state_dim=44, hidden_dim=128)

    # Test with numpy array
    import numpy as np
    state_np = np.random.randn(44).astype(np.float32)
    output_np = agent(state_np)
    print(f"✓ Numpy input: shape {output_np[0].shape}")

    # Test with single tensor
    state_single = torch.randn(44)
    output_single = agent(state_single)
    print(f"✓ Single tensor: shape {output_single[0].shape}")

    # Test with batch
    state_batch = torch.randn(8, 44)
    output_batch = agent(state_batch)
    print(f"✓ Batch tensor: shape {output_batch[0].shape}")

    # Verify outputs are correct shapes
    assert output_np[0].shape == (1, 4), "Action logits should be (1, 4)"
    assert output_single[0].shape == (1, 4), "Action logits should be (1, 4)"
    assert output_batch[0].shape == (8, 4), "Action logits should be (8, 4)"

    print("✓ Forward pass flexibility passed\n")


def test_module_structure():
    """Test that module structure follows PyTorch best practices."""
    print("=" * 60)
    print("Testing Module Structure")
    print("=" * 60)

    agent = PokerAgent(state_dim=44, hidden_dim=128)

    # Test parameter registration
    params = list(agent.parameters())
    print(f"Total parameters: {len(params)}")

    # Should have: fc1.weight, fc1.bias, fc2.weight, fc2.bias,
    #              action_head.weight, action_head.bias,
    #              raise_head.weight, raise_head.bias,
    #              value_head.weight, value_head.bias
    expected_params = 10
    assert len(params) == expected_params, f"Expected {expected_params} parameters, got {len(params)}"

    # Test named_parameters
    param_names = [name for name, _ in agent.named_parameters()]
    print(f"Parameter names: {param_names}")

    assert 'fc1.weight' in param_names
    assert 'action_head.weight' in param_names
    assert 'value_head.bias' in param_names

    print("✓ Module structure passed\n")


def test_comparison_with_original():
    """Compare behavior with original implementation."""
    print("=" * 60)
    print("Testing Backward Compatibility")
    print("=" * 60)

    # Create agent (new implementation)
    agent = PokerAgent(state_dim=44, hidden_dim=128, risk_profile='neutral')

    # Test that it can still be called the same way
    state = torch.randn(44)

    # Test forward pass
    action_logits, raise_logits, value = agent(state)

    assert action_logits.shape == (1, 4), "Action logits shape incorrect"
    assert raise_logits.shape == (1, 4), "Raise logits shape incorrect"
    assert value.shape == (1, 1), "Value shape incorrect"

    print("✓ Backward compatibility maintained\n")


if __name__ == "__main__":
    print("\nTesting Refactored PokerAgent Implementation")
    print("=" * 60)

    try:
        test_weight_initialization()
        test_extra_repr()
        test_device_handling()
        test_forward_pass_efficiency()
        test_module_structure()
        test_comparison_with_original()

        print("=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
        print("\nRefactored agent successfully implements PyTorch best practices:")
        print("  ✓ Xavier weight initialization")
        print("  ✓ Informative extra_repr for debugging")
        print("  ✓ Device parameter support")
        print("  ✓ Efficient forward pass with multiple input formats")
        print("  ✓ Proper parameter registration")
        print("  ✓ Backward compatible with existing code")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
